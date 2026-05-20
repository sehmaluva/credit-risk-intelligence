from django.db import models

from apps.loans.models import LoanApplication


class ModelVersion(models.Model):
    version = models.CharField(max_length=50, unique=True)
    mlflow_run_id = models.CharField(max_length=100, blank=True)
    metrics = models.JSONField(default=dict)
    artifact_path = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.version} (active={self.is_active})"

    def save(self, *args, **kwargs):
        if self.is_active:
            ModelVersion.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class PredictionResult(models.Model):
    application = models.ForeignKey(
        LoanApplication, on_delete=models.CASCADE, related_name="predictions"
    )
    model_version = models.ForeignKey(ModelVersion, on_delete=models.PROTECT)
    default_probability = models.FloatField()
    risk_category = models.CharField(max_length=20)
    confidence_score = models.FloatField(default=0)
    recommendation = models.CharField(max_length=50)
    recommendation_rationale = models.JSONField(default=dict)
    feature_snapshot_hash = models.CharField(max_length=64, blank=True)
    latency_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["risk_category", "created_at"])]


class RiskFactor(models.Model):
    prediction = models.ForeignKey(
        PredictionResult, on_delete=models.CASCADE, related_name="risk_factors"
    )
    feature_name = models.CharField(max_length=100)
    shap_value = models.FloatField()
    direction = models.CharField(max_length=20)
    rank = models.IntegerField()

    class Meta:
        ordering = ["rank"]
