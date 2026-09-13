# Foydalanuvchi modeli - rol, telefon va telegram_id bilan

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('nazoratchi', 'Nazoratchi'),
        ('abonent', 'Abonent'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='abonent')
    phone = models.CharField(max_length=20, unique=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return f"{self.username} ({self.role})"