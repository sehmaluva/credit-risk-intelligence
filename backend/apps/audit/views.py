from django_filters import rest_framework as filters
from rest_framework import viewsets

from apps.users.permissions import IsAdminOrRiskManager

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogFilter(filters.FilterSet):
    action = filters.CharFilter()
    resource_type = filters.CharFilter()

    class Meta:
        model = AuditLog
        fields = ["action", "resource_type"]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("actor").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrRiskManager]
    filterset_class = AuditLogFilter
    search_fields = ["action", "resource_type", "actor__email"]
