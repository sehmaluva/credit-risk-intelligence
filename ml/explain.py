"""SHAP explainability for LightGBM models."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import shap


def build_explainer(model, background: pd.DataFrame | None = None):
    """Build SHAP explainer for LightGBM with categorical splits."""
    try:
        if background is not None:
            return shap.TreeExplainer(model, data=background)
    except Exception:
        pass
    return shap.TreeExplainer(model, feature_perturbation="tree_path_dependent")


def explain_prediction(
    explainer,
    features: pd.DataFrame,
    feature_names: list[str],
    limit: int = 8,
) -> list[dict[str, Any]]:
    shap_values = explainer.shap_values(features)
    if isinstance(shap_values, list):
        shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
    values = shap_values[0] if hasattr(shap_values, "shape") and len(shap_values.shape) > 1 else shap_values

    ranked = sorted(
        zip(feature_names, values),
        key=lambda x: abs(x[1]),
        reverse=True,
    )[:limit]

    factors = []
    for rank, (name, val) in enumerate(ranked, start=1):
        factors.append(
            {
                "feature_name": name,
                "shap_value": round(float(val), 5),
                "direction": "increases_risk" if val > 0 else "decreases_risk",
                "rank": rank,
            }
        )
    return factors


def shap_waterfall_data(factors: list[dict], base_value: float = 0.0) -> list[dict]:
    """Format for Recharts waterfall."""
    data = [{"name": "Base", "value": base_value}]
    running = base_value
    for f in factors:
        running += f["shap_value"]
        data.append({"name": f["feature_name"], "value": f["shap_value"], "running": running})
    data.append({"name": "Prediction", "value": running})
    return data
