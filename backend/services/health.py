from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health_check(request):
    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False

    model_ok = False
    try:
        from ml.inference import is_model_loaded

        model_ok = is_model_loaded()
    except Exception:
        model_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse(
        {
            "status": "healthy" if db_ok and model_ok else "degraded",
            "database": db_ok,
            "model_loaded": model_ok,
        },
        status=status_code,
    )
