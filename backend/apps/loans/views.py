from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.audit.models import AuditLog
from apps.users.permissions import IsLoanOfficer, IsRiskManager
from services.scoring import score_loan_application

from .models import LoanApplication
from .serializers import LoanApplicationSerializer


class LoanApplicationFilter(filters.FilterSet):
    status = filters.CharFilter()
    province = filters.CharFilter()
    branch = filters.CharFilter()

    class Meta:
        model = LoanApplication
        fields = ["status", "province", "branch", "product_code"]


class LoanApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = LoanApplicationSerializer
    filterset_class = LoanApplicationFilter
    search_fields = ["external_id", "province", "employment_sector"]
    ordering_fields = ["created_at", "amount_usd"]

    def get_permissions(self):
        if self.action in ("destroy",):
            return [IsRiskManager()]
        return [IsLoanOfficer()]

    def get_queryset(self):
        qs = LoanApplication.objects.select_related("created_by").prefetch_related("predictions")
        user = self.request.user
        if user.role in ("admin", "risk_manager"):
            return qs
        from django.db.models import Q
        return qs.filter(Q(created_by=user) | Q(branch=user.branch))

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.status != LoanApplication.Status.DRAFT:
            raise ValidationError("Only draft applications can be edited.")
        serializer.save()
        AuditLog.log(self.request, "APPLICATION_UPDATE", "loan_application", instance.id)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        app = self.get_object()
        if app.status != LoanApplication.Status.DRAFT:
            return Response({"detail": "Only draft can be submitted."}, status=400)
        app.status = LoanApplication.Status.SUBMITTED
        app.save(update_fields=["status", "updated_at"])
        AuditLog.log(request, "APPLICATION_SUBMIT", "loan_application", app.id)
        return Response(self.get_serializer(app).data)

    @action(detail=True, methods=["post"])
    def score(self, request, pk=None):
        app = self.get_object()
        if app.status not in (LoanApplication.Status.SUBMITTED, LoanApplication.Status.SCORED):
            return Response({"detail": "Application must be submitted before scoring."}, status=400)
        result = score_loan_application(app, request)
        app.status = LoanApplication.Status.SCORED
        app.save(update_fields=["status", "updated_at"])
        AuditLog.log(request, "SCORE", "loan_application", app.id, {"prediction_id": result.id})
        from apps.predictions.serializers import PredictionResultSerializer

        return Response(PredictionResultSerializer(result).data, status=status.HTTP_201_CREATED)
