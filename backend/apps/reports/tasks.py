import csv
import io
from datetime import datetime

from celery import shared_task
from django.core.files.base import ContentFile

from apps.audit.models import AuditLog
from apps.loans.models import LoanApplication
from apps.predictions.models import PredictionResult

from .models import Report


@shared_task
def generate_report_task(report_id: int):
    report = Report.objects.get(pk=report_id)
    report.status = Report.Status.PROCESSING
    report.save(update_fields=["status"])

    try:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        if report.type == Report.ReportType.PORTFOLIO_SUMMARY:
            writer.writerow(["external_id", "status", "amount_usd", "province", "risk_category", "probability"])
            for app in LoanApplication.objects.all()[:500]:
                pred = app.predictions.order_by("-created_at").first()
                writer.writerow([
                    app.external_id,
                    app.status,
                    app.amount_usd,
                    app.province,
                    pred.risk_category if pred else "",
                    pred.default_probability if pred else "",
                ])
        else:
            writer.writerow(["action", "resource_type", "actor", "created_at"])
            for log in AuditLog.objects.all()[:500]:
                writer.writerow([
                    log.action,
                    log.resource_type,
                    log.actor.email if log.actor else "",
                    log.created_at.isoformat(),
                ])
        content = buffer.getvalue().encode("utf-8")
        filename = f"{report.type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        report.file.save(filename, ContentFile(content))
        report.status = Report.Status.COMPLETED
        report.completed_at = datetime.utcnow()
        report.save()
    except Exception as e:
        report.status = Report.Status.FAILED
        report.error_message = str(e)
        report.save()
