"""Rule-based recommendation engine for credit decisions."""

from __future__ import annotations

from typing import Any


RISK_THRESHOLDS = [
    (0.20, "low"),
    (0.50, "medium"),
    (0.75, "high"),
    (1.01, "critical"),
]


def classify_risk(probability: float) -> str:
    for threshold, label in RISK_THRESHOLDS:
        if probability < threshold:
            return label
    return "critical"


def compute_confidence(probability: float, top_shap: list[dict]) -> float:
    margin = abs(probability - 0.5) * 2
    shap_strength = min(1.0, sum(abs(f.get("shap_value", 0)) for f in top_shap[:5]) / 2.0)
    return round(min(0.99, 0.5 * margin + 0.5 * shap_strength), 3)


def generate_recommendation(
    probability: float,
    top_factors: list[dict[str, Any]],
    application: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    category = classify_risk(probability)
    obligations = float(application.get("existing_obligations") or 0)
    collateral = str(application.get("collateral_type") or "None")
    income = float(application.get("monthly_income_usd") or 0)
    amount = float(application.get("amount_usd") or 0)
    dti = amount / income if income > 0 else 999

    rationale: list[str] = []
    recommendation = "approve"

    if probability >= 0.75:
        recommendation = "reject"
        rationale.append(f"Default probability {probability:.1%} exceeds critical threshold.")
    elif probability >= 0.50:
        if obligations >= 4:
            recommendation = "shorten_repayment_duration"
            rationale.append("High existing obligations with elevated default risk.")
        elif collateral in ("None", "Unknown") or collateral == "":
            recommendation = "require_guarantor"
            rationale.append("Weak collateral profile with high default probability.")
        else:
            recommendation = "reduce_amount"
            rationale.append("Elevated risk — recommend reducing loan amount.")
    elif probability >= 0.20:
        if dti > 0.5:
            recommendation = "reduce_amount"
            rationale.append(f"Debt-to-income ratio ({dti:.2f}) is elevated for medium risk.")
        else:
            recommendation = "approve_with_monitoring"
            rationale.append("Medium risk — approve with enhanced portfolio monitoring.")
    else:
        recommendation = "approve"
        rationale.append("Low default probability — within acceptable risk appetite.")

    if top_factors:
        top_name = top_factors[0].get("feature_name", "")
        rationale.append(f"Primary risk driver: {top_name.replace('_', ' ')}.")

    return recommendation, {
        "category": category,
        "probability": round(probability, 4),
        "rationale": rationale,
        "top_factors": top_factors[:5],
    }
