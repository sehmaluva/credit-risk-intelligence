from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import IsAdminOrRiskManager, IsLoanOfficer

from .models import ModelVersion, PredictionResult
from .serializers import ModelVersionSerializer, PredictionResultSerializer
from services.scoring import get_shap_waterfall


class PredictionFilter(filters.FilterSet):
    risk_category = filters.CharFilter()
    application = filters.NumberFilter()

    class Meta:
        model = PredictionResult
        fields = ["risk_category", "application"]


class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PredictionResultSerializer
    filterset_class = PredictionFilter
    permission_classes = [IsLoanOfficer]

    def get_queryset(self):
        return PredictionResult.objects.select_related(
            "application", "model_version"
        ).prefetch_related("risk_factors")

    @action(detail=True, methods=["get"])
    def shap(self, request, pk=None):
        prediction = self.get_object()
        return Response(get_shap_waterfall(prediction))


class ModelVersionViewSet(viewsets.ModelViewSet):
    queryset = ModelVersion.objects.all()
    serializer_class = ModelVersionSerializer
    permission_classes = [IsAdminOrRiskManager]

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        mv = self.get_object()
        mv.is_active = True
        mv.save()
        return Response(self.get_serializer(mv).data)
