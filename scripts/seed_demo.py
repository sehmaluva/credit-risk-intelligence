#!/usr/bin/env python
"""Seed demo users and sample loan applications."""
import argparse
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

import django

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from apps.loans.models import LoanApplication  # noqa: E402
from apps.predictions.models import ModelVersion  # noqa: E402
from apps.users.models import User  # noqa: E402

DEMO_USERS = [
    ("admin@creditrisk.io", "admin123", User.Role.ADMIN, "HQ"),
    ("risk@creditrisk.io", "risk123", User.Role.RISK_MANAGER, "HQ"),
    ("officer@creditrisk.io", "officer123", User.Role.LOAN_OFFICER, "Harare"),
]

PROVINCES = [
    "Harare", "Bulawayo", "Manicaland", "Mashonaland_West",
    "Mashonaland_East", "Midlands", "Masvingo",
]
SECTORS = ["Agriculture", "Retail_Trade", "Government", "Informal_Sector", "Healthcare"]
PURPOSES = ["Working_Capital", "Farming_Inputs", "School_Fees", "Medical", "Business_Expansion"]


def ensure_users():
    for email, password, role, branch in DEMO_USERS:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email.split("@")[0], "role": role, "branch": branch},
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"Created user: {email} / {password}")


def ensure_model_version():
    ModelVersion.objects.get_or_create(
        version="v1.0.0",
        defaults={"metrics": {"oof_auc": 0.68}, "is_active": True},
    )


def seed_applications(count=30):
    officer = User.objects.filter(role=User.Role.LOAN_OFFICER).first()
    if not officer:
        return
    if LoanApplication.objects.count() >= count:
        return
    for i in range(count):
        income = random.uniform(200, 2500)
        amount = random.uniform(100, min(15000, income * 12))
        LoanApplication.objects.create(
            external_id=f"DEMO{i:04d}",
            status=random.choice([
                LoanApplication.Status.DRAFT,
                LoanApplication.Status.SUBMITTED,
                LoanApplication.Status.SCORED,
            ]),
            created_by=officer,
            branch=officer.branch,
            product_code=random.randint(0, 5),
            date_approved=date.today() - timedelta(days=random.randint(1, 90)),
            date_disbursed=date.today() - timedelta(days=random.randint(0, 60)),
            first_payment_due=date.today() + timedelta(days=30),
            maturity_date=date.today() + timedelta(days=random.randint(180, 720)),
            amount_usd=round(amount, 2),
            annual_rate_pct=round(random.uniform(12, 120), 2),
            term_months=random.choice([6, 12, 18, 24, 36]),
            payment_frequency=random.choice(["Monthly", "Bi-Weekly", "Weekly"]),
            loan_purpose=random.choice(PURPOSES),
            client_gender=random.choice(["Male", "Female"]),
            client_dob=date(1970, 1, 1) + timedelta(days=random.randint(7000, 18000)),
            marital_status=random.choice(["Married", "Single", "Divorced"]),
            num_dependents=random.randint(0, 5),
            employment_sector=random.choice(SECTORS),
            months_at_employer=random.randint(1, 120),
            monthly_income_usd=round(income, 2),
            existing_obligations=random.randint(0, 5),
            collateral_type=random.choice(["None", "Vehicle", "Property", "Guarantor"]),
            disbursement_channel=random.choice(["EcoCash", "Bank_Transfer", "Cash"]),
            province=random.choice(PROVINCES),
        )
    print(f"Seeded {count} demo applications")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--if-empty", action="store_true")
    args = parser.parse_args()
    if args.if_empty and User.objects.filter(email=DEMO_USERS[0][0]).exists():
        print("Demo data already exists, skipping.")
        return
    ensure_users()
    ensure_model_version()
    seed_applications()


if __name__ == "__main__":
    main()
