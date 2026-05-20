from django.conf import settings
from django.db import models


class LoanApplication(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        SCORED = "scored", "Scored"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    external_id = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="applications"
    )
    branch = models.CharField(max_length=100, default="Main")

    product_code = models.IntegerField(default=0)
    date_approved = models.DateField(null=True, blank=True)
    date_disbursed = models.DateField(null=True, blank=True)
    first_payment_due = models.DateField(null=True, blank=True)
    maturity_date = models.DateField(null=True, blank=True)
    amount_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    annual_rate_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    term_months = models.IntegerField(default=12)
    payment_frequency = models.CharField(max_length=20, default="Monthly")
    loan_purpose = models.CharField(max_length=50, blank=True)
    client_gender = models.CharField(max_length=10, default="Male")
    client_dob = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, default="Single")
    num_dependents = models.IntegerField(default=0)
    employment_sector = models.CharField(max_length=50, blank=True)
    months_at_employer = models.IntegerField(default=0)
    monthly_income_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    existing_obligations = models.IntegerField(default=0)
    collateral_type = models.CharField(max_length=30, default="None")
    disbursement_channel = models.CharField(max_length=30, default="Bank_Transfer")
    province = models.CharField(max_length=50, default="Harare")

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return self.external_id or f"APP-{self.pk}"

    def to_feature_dict(self) -> dict:
        return {
            "product_code": self.product_code,
            "date_approved": str(self.date_approved) if self.date_approved else None,
            "date_disbursed": str(self.date_disbursed) if self.date_disbursed else None,
            "first_payment_due": str(self.first_payment_due) if self.first_payment_due else None,
            "maturity_date": str(self.maturity_date) if self.maturity_date else None,
            "amount_usd": float(self.amount_usd),
            "annual_rate_pct": float(self.annual_rate_pct),
            "term_months": self.term_months,
            "payment_frequency": self.payment_frequency,
            "loan_purpose": self.loan_purpose,
            "client_gender": self.client_gender,
            "client_dob": str(self.client_dob) if self.client_dob else None,
            "marital_status": self.marital_status,
            "num_dependents": self.num_dependents,
            "employment_sector": self.employment_sector,
            "months_at_employer": self.months_at_employer,
            "monthly_income_usd": float(self.monthly_income_usd),
            "existing_obligations": self.existing_obligations,
            "collateral_type": self.collateral_type,
            "disbursement_channel": self.disbursement_channel,
            "province": self.province,
        }
