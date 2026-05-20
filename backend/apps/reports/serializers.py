from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "type",
            "params",
            "status",
            "file",
            "file_url",
            "created_by",
            "created_by_email",
            "created_at",
            "completed_at",
            "error_message",
        ]
        read_only_fields = ["status", "file", "created_by", "created_at", "completed_at", "error_message"]

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
