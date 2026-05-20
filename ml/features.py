"""Shared feature engineering pipeline for training and inference."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ID_COL = "ID"
TARGET_COL = "Target"

DATE_COLS = [
    "date_approved",
    "date_disbursed",
    "first_payment_due",
    "maturity_date",
    "client_dob",
]

CAT_COLS = [
    "product_code",
    "payment_frequency",
    "loan_purpose",
    "client_gender",
    "marital_status",
    "employment_sector",
    "collateral_type",
    "disbursement_channel",
    "province",
]

NUM_COLS = [
    "amount_usd",
    "annual_rate_pct",
    "term_months",
    "num_dependents",
    "months_at_employer",
    "monthly_income_usd",
    "existing_obligations",
]

# Application field mapping (API -> training columns)
APPLICATION_FIELDS = [
    "product_code",
    "date_approved",
    "date_disbursed",
    "first_payment_due",
    "maturity_date",
    "amount_usd",
    "annual_rate_pct",
    "term_months",
    "payment_frequency",
    "loan_purpose",
    "client_gender",
    "client_dob",
    "marital_status",
    "num_dependents",
    "employment_sector",
    "months_at_employer",
    "monthly_income_usd",
    "existing_obligations",
    "collateral_type",
    "disbursement_channel",
    "province",
]


def normalize_target_column(df: pd.DataFrame) -> pd.DataFrame:
    if TARGET_COL in df.columns:
        return df
    lc_map = {c.lower(): c for c in df.columns}
    for alt in ["target", "defaulted", "default", "label", "y"]:
        if alt in lc_map:
            df = df.rename(columns={lc_map[alt]: TARGET_COL})
            break
    return df


def parse_dates(df: pd.DataFrame, date_cols: list[str] | None = None) -> pd.DataFrame:
    date_cols = date_cols or DATE_COLS
    df = df.copy()
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
    return df


def add_date_features(df: pd.DataFrame, date_cols: list[str] | None = None) -> pd.DataFrame:
    date_cols = date_cols or DATE_COLS
    df = df.copy()
    if "date_disbursed" in df.columns and "date_approved" in df.columns:
        df["days_approval_to_disb"] = (
            df["date_disbursed"] - df["date_approved"]
        ).dt.days
    if "first_payment_due" in df.columns and "date_disbursed" in df.columns:
        df["days_disb_to_first_pay"] = (
            df["first_payment_due"] - df["date_disbursed"]
        ).dt.days
    if "maturity_date" in df.columns and "date_disbursed" in df.columns:
        df["loan_duration_days"] = (df["maturity_date"] - df["date_disbursed"]).dt.days
    if "client_dob" in df.columns and "date_approved" in df.columns:
        df["borrower_age_years"] = (
            (df["date_approved"] - df["client_dob"]).dt.days / 365.25
        )
    for col in date_cols:
        if col not in df.columns or not df[col].notna().any():
            continue
        df[f"{col}_month"] = df[col].dt.month
        df[f"{col}_month_sin"] = np.sin(2 * np.pi * df[f"{col}_month"] / 12)
        df[f"{col}_month_cos"] = np.cos(2 * np.pi * df[f"{col}_month"] / 12)
        df[f"{col}_dayofweek"] = df[col].dt.dayofweek
        df[f"{col}_dayofweek_sin"] = np.sin(2 * np.pi * df[f"{col}_dayofweek"] / 7)
        df[f"{col}_dayofweek_cos"] = np.cos(2 * np.pi * df[f"{col}_dayofweek"] / 7)
    return df


def add_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "monthly_income_usd" in df.columns and "amount_usd" in df.columns:
        income = df["monthly_income_usd"].replace(0, np.nan)
        df["debt_to_income"] = df["amount_usd"] / income
    if "term_months" in df.columns and "amount_usd" in df.columns and "monthly_income_usd" in df.columns:
        monthly_payment = df["amount_usd"] / df["term_months"].replace(0, np.nan)
        income = df["monthly_income_usd"].replace(0, np.nan)
        df["repayment_burden"] = monthly_payment / income
    if "num_dependents" in df.columns and "monthly_income_usd" in df.columns:
        deps = df["num_dependents"].replace(0, 1)
        df["income_per_dependent"] = df["monthly_income_usd"] / deps
    return df


def prepare_categoricals(
    train: pd.DataFrame,
    test: pd.DataFrame | None = None,
    cat_cols: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame | None, list[str]]:
    train = train.copy()
    test = test.copy() if test is not None else None
    auto_cat = [
        c
        for c in train.columns
        if c not in [ID_COL, TARGET_COL]
        and (
            pd.api.types.is_object_dtype(train[c])
            or isinstance(train[c].dtype, pd.CategoricalDtype)
        )
    ]
    all_cat_cols = sorted(set((cat_cols or CAT_COLS) + auto_cat))
    all_cat_cols = [c for c in all_cat_cols if c in train.columns]

    for col in all_cat_cols:
        for frame in ([train] + ([test] if test is not None else [])):
            frame[col] = (
                frame[col]
                .where(frame[col].notna(), "Unknown")
                .astype(str)
                .replace(["nan", "NaN", "None", "<NA>", "NaT"], "Unknown")
            )
        if test is not None:
            combined = pd.concat([train[col], test[col]], axis=0)
        else:
            combined = train[col]
        categories = pd.Index(combined).dropna().unique()
        if len(categories) == 0:
            categories = pd.Index(["Unknown"])
        train[col] = pd.Categorical(train[col], categories=categories)
        if test is not None:
            test[col] = pd.Categorical(test[col], categories=categories)

    return train, test, all_cat_cols


def application_to_dataframe(application: dict[str, Any]) -> pd.DataFrame:
    """Convert API application dict to single-row DataFrame."""
    row = {k: application.get(k) for k in APPLICATION_FIELDS}
    return pd.DataFrame([row])


def build_features(
    df: pd.DataFrame,
    category_manifest: dict[str, list[str]] | None = None,
    drop_target: bool = True,
) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Full pipeline: dates -> financial -> drop dates -> categoricals -> feature list."""
    df = df.copy()
    df = normalize_target_column(df)
    df = parse_dates(df)
    df = add_date_features(df)
    df = add_financial_features(df)

    for col in DATE_COLS:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    if category_manifest:
        for col, cats in category_manifest.items():
            if col in df.columns:
                df[col] = df[col].astype(str).replace(
                    ["nan", "NaN", "None", "<NA>", "NaT"], "Unknown"
                )
                df[col] = pd.Categorical(df[col], categories=cats)
        cat_cols = list(category_manifest.keys())
    else:
        df, _, cat_cols = prepare_categoricals(df, None)

    exclude = [ID_COL]
    if drop_target and TARGET_COL in df.columns:
        exclude.append(TARGET_COL)

    numeric_features = [
        c
        for c in df.columns
        if c not in cat_cols + exclude and pd.api.types.is_numeric_dtype(df[c])
    ]
    features = numeric_features + cat_cols
    return df[features], features, cat_cols


def get_cat_feature_indices(features: list[str], cat_cols: list[str]) -> list[int]:
    return [features.index(c) for c in cat_cols if c in features]


def save_manifest(
    path: Path,
    features: list[str],
    cat_cols: list[str],
    category_manifest: dict[str, list[str]],
    metrics: dict[str, float] | None = None,
) -> None:
    manifest = {
        "features": features,
        "cat_cols": cat_cols,
        "category_manifest": category_manifest,
        "metrics": metrics or {},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2))

def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())
