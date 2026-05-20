from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.loans.models import LoanApplication
from apps.predictions.models import PredictionResult
from apps.users.permissions import IsLoanOfficer


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsLoanOfficer]

    @action(detail=False, methods=["get"])
    def overview(self, request):
        apps = LoanApplication.objects.all()
        preds = PredictionResult.objects.all()
        total = apps.count()
        scored = apps.filter(status=LoanApplication.Status.SCORED).count()
        approved = apps.filter(status=LoanApplication.Status.APPROVED).count()
        risk_dist = (
            preds.values("risk_category")
            .annotate(count=Count("id"))
            .order_by("risk_category")
        )
        avg_prob = preds.aggregate(avg=Avg("default_probability"))["avg"] or 0
        return Response(
            {
                "total_applications": total,
                "scored_applications": scored,
                "approval_rate": round(approved / total, 3) if total else 0,
                "portfolio_health_score": round(1 - float(avg_prob), 3),
                "avg_default_probability": round(float(avg_prob), 4),
                "risk_distribution": {r["risk_category"]: r["count"] for r in risk_dist},
            }
        )

    @action(detail=False, methods=["get"])
    def trends(self, request):
        trends = (
            PredictionResult.objects.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(
                count=Count("id"),
                avg_probability=Avg("default_probability"),
            )
            .order_by("day")[:30]
        )
        return Response(list(trends))

    @action(detail=False, methods=["get"])
    def defaults(self, request):
        by_province = (
            PredictionResult.objects.select_related("application")
            .values("application__province")
            .annotate(
                count=Count("id"),
                avg_probability=Avg("default_probability"),
            )
            .order_by("-avg_probability")[:15]
        )
        by_product = (
            PredictionResult.objects.select_related("application")
            .values("application__product_code")
            .annotate(
                count=Count("id"),
                avg_probability=Avg("default_probability"),
            )
            .order_by("application__product_code")
        )
        return Response({"by_province": list(by_province), "by_product": list(by_product)})
