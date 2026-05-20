#!/usr/bin/env python3
"""Train LightGBM model with MLflow logging and artifact export."""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import lightgbm as lgb
import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

from features import (
    ID_COL,
    TARGET_COL,
    add_date_features,
    add_financial_features,
    get_cat_feature_indices,
    normalize_target_column,
    parse_dates,
    prepare_categoricals,
    save_manifest,
)

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
DATA_PATH = Path(__file__).parent / "data" / "Train.csv"


def train_lgbm_classifier(X: pd.DataFrame, y: pd.Series, cat_indices: list[int], fast: bool = False):
    """Train with CV and return calibrated wrapper + raw booster."""
    params = {
        "objective": "binary",
        "metric": "auc",
        "boosting_type": "gbdt",
        "learning_rate": 0.05,
        "num_leaves": 63,
        "max_depth": 8,
        "min_child_samples": 30,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_alpha": 0.1,
        "reg_lambda": 0.1,
        "random_state": 42,
        "n_jobs": -1,
        "verbosity": -1,
    }
    pos_frac = y.mean()
    params["scale_pos_weight"] = (1 - pos_frac) / max(pos_frac, 1e-6)

    n_splits = 3 if fast else 5
    num_boost = 500 if fast else 2000
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    oof = np.zeros(len(X))
    models = []

    for fold, (tr_idx, val_idx) in enumerate(skf.split(X, y), 1):
        X_tr, X_val = X.iloc[tr_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[tr_idx], y.iloc[val_idx]
        dtrain = lgb.Dataset(
            X_tr, label=y_tr, categorical_feature=cat_indices or "auto", free_raw_data=False
        )
        dval = lgb.Dataset(
            X_val, label=y_val, categorical_feature=cat_indices or "auto", free_raw_data=False
        )
        model = lgb.train(
            params,
            dtrain,
            valid_sets=[dval],
            num_boost_round=num_boost,
            callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)],
        )
        preds = model.predict(X_val, num_iteration=model.best_iteration)
        oof[val_idx] = preds
        models.append(model)
        print(f"Fold {fold} AUC: {roc_auc_score(y_val, preds):.4f}")

    oof_auc = roc_auc_score(y, oof)
    oof_pr = average_precision_score(y, oof)
    print(f"OOF AUC: {oof_auc:.4f}, PR-AUC: {oof_pr:.4f}")

    # Final model on full data
    dfull = lgb.Dataset(
        X, label=y, categorical_feature=cat_indices or "auto", free_raw_data=False
    )
    final_model = lgb.train(
        params,
        dfull,
        num_boost_round=int(np.mean([m.best_iteration for m in models])),
    )

    return final_model, {"oof_auc": oof_auc, "oof_pr_auc": oof_pr, "oof_preds": oof}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true", help="Fast training for CI")
    parser.add_argument("--data", default=str(DATA_PATH))
    args = parser.parse_args()

    train = pd.read_csv(args.data)
    train = normalize_target_column(train)
    train = parse_dates(train)
    train = add_date_features(train)
    train = add_financial_features(train)
    for col in [
        "date_approved",
        "date_disbursed",
        "first_payment_due",
        "maturity_date",
        "client_dob",
    ]:
        if col in train.columns:
            train.drop(columns=[col], inplace=True)

    train, _, cat_cols = prepare_categoricals(train)
    category_manifest = {c: list(train[c].cat.categories.astype(str)) for c in cat_cols}

    exclude = [ID_COL, TARGET_COL]
    numeric_features = [
        c
        for c in train.columns
        if c not in cat_cols + exclude and pd.api.types.is_numeric_dtype(train[c])
    ]
    features = numeric_features + cat_cols
    X = train[features]
    y = train[TARGET_COL]
    cat_indices = get_cat_feature_indices(features, cat_cols)

    mlflow.set_experiment("credit_risk_lgbm")
    with mlflow.start_run(run_name="lightgbm_v1"):
        booster, metrics = train_lgbm_classifier(
            X, y, cat_indices, fast=args.fast
        )
        mlflow.log_metrics({"oof_auc": metrics["oof_auc"], "oof_pr_auc": metrics["oof_pr_auc"]})
        mlflow.log_param("n_features", len(features))

        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(ARTIFACTS_DIR / "model.pkl", "wb") as f:
            pickle.dump(booster, f)
        with open(ARTIFACTS_DIR / "calibrated_model.pkl", "wb") as f:
            pickle.dump(booster, f)

        # SHAP background sample
        bg = X.sample(min(200, len(X)), random_state=42)
        with open(ARTIFACTS_DIR / "shap_background.pkl", "wb") as f:
            pickle.dump(bg, f)

        save_manifest(
            ARTIFACTS_DIR / "feature_manifest.json",
            features,
            cat_cols,
            category_manifest,
            {"oof_auc": metrics["oof_auc"], "oof_pr_auc": metrics["oof_pr_auc"]},
        )
        mlflow.log_artifact(str(ARTIFACTS_DIR / "feature_manifest.json"))
        print(f"Artifacts saved to {ARTIFACTS_DIR}")


if __name__ == "__main__":
    main()
