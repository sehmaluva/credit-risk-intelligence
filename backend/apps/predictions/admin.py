from django.contrib import admin

from .models import ModelVersion, PredictionResult, RiskFactor

admin.site.register(ModelVersion)
admin.site.register(PredictionResult)
admin.site.register(RiskFactor)
