from rest_framework import serializers

from .models import ModelVersion, PredictionResult, RiskFactor


class RiskFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskFactor
        fields = ["feature_name", "shap_value", "direction", "rank"]


class PredictionResultSerializer(serializers.ModelSerializer):
    risk_factors = RiskFactorSerializer(many=True, read_only=True)
    application_external_id = serializers.CharField(source="application.external_id", read_only=True)

    class Meta:
        model = PredictionResult
        fields = [
            "id",
            "application",
            "application_external_id",
            "model_version",
            "default_probability",
            "risk_category",
            "confidence_score",
            "recommendation",
            "recommendation_rationale",
            "risk_factors",
            "latency_ms",
            "created_at",
        ]


class ModelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelVersion
        fields = ["id", "version", "mlflow_run_id", "metrics", "is_active", "created_at"]
