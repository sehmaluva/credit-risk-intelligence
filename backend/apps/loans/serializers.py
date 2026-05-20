from rest_framework import serializers

from .models import LoanApplication


class LoanApplicationSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    latest_prediction = serializers.SerializerMethodField()

    class Meta:
        model = LoanApplication
        fields = [
            "id",
            "external_id",
            "status",
            "created_by",
            "created_by_email",
            "branch",
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
            "notes",
            "created_at",
            "updated_at",
            "latest_prediction",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at", "status"]

    def get_latest_prediction(self, obj):
        pred = obj.predictions.order_by("-created_at").first()
        if not pred:
            return None
        return {
            "id": pred.id,
            "default_probability": pred.default_probability,
            "risk_category": pred.risk_category,
            "recommendation": pred.recommendation,
        }

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by"] = request.user
        validated_data["branch"] = request.user.branch
        import uuid

        validated_data.setdefault("external_id", f"CR{uuid.uuid4().hex[:8].upper()}")
        return super().create(validated_data)
