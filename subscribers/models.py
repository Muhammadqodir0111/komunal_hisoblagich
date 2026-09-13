# Abonent, xizmat turi va hisoblagich modellari

from django.db import models
from django.conf import settings


class ServiceType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    unit = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscriber(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subscriber'
    )
    account_number = models.CharField(max_length=12, unique=True, db_index=True)
    full_name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.account_number} - {self.full_name}"


class Meter(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='meters')
    service = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=30, unique=True)
    installed_at = models.DateField()
    initial_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('subscriber', 'service')

    def __str__(self):
        return f"{self.serial_number} ({self.service.name})"