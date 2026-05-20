from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.analytics.views import AnalyticsViewSet
from apps.audit.views import AuditLogViewSet
from apps.authentication.views import LoginView, LogoutView, MeView
from apps.loans.views import LoanApplicationViewSet
from apps.predictions.views import ModelVersionViewSet, PredictionViewSet
from apps.reports.views import ReportViewSet
from apps.users.views import UserViewSet
from services.health import health_check

router = DefaultRouter()
router.register(r"applications", LoanApplicationViewSet, basename="application")
router.register(r"predictions", PredictionViewSet, basename="prediction")
router.register(r"model-versions", ModelVersionViewSet, basename="model-version")
router.register(r"users", UserViewSet, basename="user")
router.register(r"audit/logs", AuditLogViewSet, basename="audit-log")
router.register(r"reports", ReportViewSet, basename="report")

analytics_router = DefaultRouter()
analytics_router.register(r"", AnalyticsViewSet, basename="analytics")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check),
    path("api/v1/auth/login/", LoginView.as_view()),
    path("api/v1/auth/logout/", LogoutView.as_view()),
    path("api/v1/auth/me/", MeView.as_view()),
    path("api/v1/auth/refresh/", TokenRefreshView.as_view()),
    path("api/v1/", include(router.urls)),
    path("api/v1/analytics/", include(analytics_router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
