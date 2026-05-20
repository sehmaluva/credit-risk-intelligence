import logging

from apps.audit.models import AuditLog
from apps.predictions.models import ModelVersion, PredictionResult, RiskFactor
logger = logging.getLogger(__name__)


def get_active_model_version() -> ModelVersion:
    mv = ModelVersion.objects.filter(is_active=True).first()
    if not mv:
        mv, _ = ModelVersion.objects.get_or_create(
            version="v1.0.0",
            defaults={"metrics": {}, "is_active": True},
        )
    return mv


def score_loan_application(application, request=None) -> PredictionResult:
    from ml.inference import score_application_dict as infer

    output = infer(application.to_feature_dict())
    mv = get_active_model_version()

    prediction = PredictionResult.objects.create(
        application=application,
        model_version=mv,
        default_probability=output.default_probability,
        risk_category=output.risk_category,
        confidence_score=output.confidence_score,
        recommendation=output.recommendation,
        recommendation_rationale=output.recommendation_rationale,
        feature_snapshot_hash=output.feature_snapshot_hash,
        latency_ms=output.latency_ms,
    )
    for factor in output.risk_factors:
        RiskFactor.objects.create(
            prediction=prediction,
            feature_name=factor["feature_name"],
            shap_value=factor["shap_value"],
            direction=factor["direction"],
            rank=factor["rank"],
        )
    logger.info(
        "prediction_scored application_id=%s prob=%.4f model=%s latency_ms=%s",
        application.id,
        output.default_probability,
        mv.version,
        output.latency_ms,
    )
    return prediction


def get_shap_waterfall(prediction: PredictionResult) -> dict:
    factors = list(
        prediction.risk_factors.order_by("rank").values(
            "feature_name", "shap_value", "direction", "rank"
        )
    )
    running = 0.0
    waterfall = []
    for f in factors:
        running += f["shap_value"]
        waterfall.append({**f, "running": round(running, 5)})
    return {
        "base_value": 0,
        "probability": prediction.default_probability,
        "factors": factors,
        "waterfall": waterfall,
    }
