from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.audit.models import AuditLog
from apps.users.permissions import IsLoanOfficer

from .models import Report
from .serializers import ReportSerializer
from .tasks import generate_report_task


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [IsLoanOfficer]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.role in ("admin", "risk_manager"):
            return Report.objects.all()
        return Report.objects.filter(created_by=user)

    def perform_create(self, serializer):
        report = serializer.save(created_by=self.request.user, status=Report.Status.PENDING)
        generate_report_task.delay(report.id)
        AuditLog.log(self.request, "REPORT_GENERATE", "report", report.id, {"type": report.type})

    @action(detail=True, methods=["post"], url_path="generate")
    def generate(self, request, pk=None):
        report = self.get_object()
        generate_report_task.delay(report.id)
        return Response(self.get_serializer(report).data)
