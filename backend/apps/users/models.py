from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        RISK_MANAGER = "risk_manager", "Risk Manager"
        LOAN_OFFICER = "loan_officer", "Loan Officer"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.LOAN_OFFICER)
    branch = models.CharField(max_length=100, blank=True, default="Main")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.role})"
