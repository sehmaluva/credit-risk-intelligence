"""Django wrapper for ML inference."""

from __future__ import annotations

import hashlib
import json
import logging
import pickle
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from django.conf import settings

from ml.explain import build_explainer, explain_prediction
from ml.features import application_to_dataframe, build_features, load_manifest
from ml.recommend import classify_risk, compute_confidence, generate_recommendation

logger = logging.getLogger(__name__)

_artifacts: dict[str, Any] = {}


@dataclass
class ScoringOutput:
    default_probability: float
    risk_category: str
    confidence_score: float
    recommendation: str
    recommendation_rationale: dict
    risk_factors: list[dict]
    feature_snapshot_hash: str
    latency_ms: int


def _artifacts_path() -> Path:
    return Path(settings.ML_ARTIFACTS_PATH)


def load_artifacts(force: bool = False) -> bool:
    if _artifacts and not force:
        return True
    path = _artifacts_path()
    manifest_path = path / "feature_manifest.json"
    model_path = path / "calibrated_model.pkl"
    bg_path = path / "shap_background.pkl"
    if not manifest_path.exists() or not model_path.exists():
        logger.warning("ML artifacts not found at %s", path)
        return False
    with open(manifest_path) as f:
        manifest = json.load(f)
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    explainer = None
    raw_path = path / "model.pkl"
    if raw_path.exists():
        with open(raw_path, "rb") as f:
            booster = pickle.load(f)
        explainer = build_explainer(booster)
    _artifacts["manifest"] = manifest
    _artifacts["model"] = model
    _artifacts["explainer"] = explainer
    _artifacts["features"] = manifest["features"]
    _artifacts["cat_cols"] = manifest["cat_cols"]
    _artifacts["category_manifest"] = manifest["category_manifest"]
    return True


def is_model_loaded() -> bool:
    return bool(_artifacts) or load_artifacts()


def score_application_dict(application: dict) -> ScoringOutput:
    start = time.time()
    if not load_artifacts():
        raise RuntimeError("ML model artifacts not loaded. Run ml/train.py first.")

    df = application_to_dataframe(application)
    X, _, _ = build_features(
        df,
        category_manifest=_artifacts["category_manifest"],
        drop_target=True,
    )
    features = _artifacts["features"]
    X = X.reindex(columns=features, fill_value=0)

    model = _artifacts["model"]
    if hasattr(model, "predict_proba"):
        prob = float(model.predict_proba(X)[0][1])
    else:
        prob = float(model.predict(X)[0])
    risk_factors = []
    if _artifacts.get("explainer"):
        risk_factors = explain_prediction(
            _artifacts["explainer"], X, features, limit=8
        )

    recommendation, rationale = generate_recommendation(prob, risk_factors, application)
    confidence = compute_confidence(prob, risk_factors)
    category = classify_risk(prob)
    snapshot_hash = hashlib.sha256(json.dumps(application, sort_keys=True, default=str).encode()).hexdigest()[:16]
    latency_ms = int((time.time() - start) * 1000)

    return ScoringOutput(
        default_probability=round(prob, 4),
        risk_category=category,
        confidence_score=confidence,
        recommendation=recommendation,
        recommendation_rationale=rationale,
        risk_factors=risk_factors,
        feature_snapshot_hash=snapshot_hash,
        latency_ms=latency_ms,
    )
