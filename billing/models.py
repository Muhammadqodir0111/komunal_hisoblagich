from django.db import models
from django.conf import settings
from subscribers.models import Subscriber, Meter, ServiceType


class Tariff(models.Model):
    service = models.ForeignKey(ServiceType, on_delete=models.PROTECT, related_name='tariffs')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField(db_index=True)
    valid_to = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.service.name} - {self.price_per_unit} ({self.valid_from})"



class Reading(models.Model):
    STATUS_CHOICES = (
        ('yuborilgan', 'Yuborilgan'),
        ('tasdiqlangan', 'Tasdiqlangan'),
        ('rad_etilgan', 'Rad etilgan'),
    )

    meter = models.ForeignKey(Meter, on_delete=models.PROTECT, related_name='readings')
    period = models.CharField(max_length=7, db_index=True)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    photo = models.ImageField(upload_to='readings/%Y/%m/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='yuborilgan')
    reject_reason = models.CharField(max_length=255, blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_readings'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_readings'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('meter', 'period')

    def __str__(self):
        return f"{self.meter} - {self.period} ({self.status})"


class Invoice(models.Model):
    reading = models.OneToOneField(Reading, on_delete=models.PROTECT, related_name='invoice')
    subscriber = models.ForeignKey(Subscriber, on_delete=models.PROTECT, related_name='invoices')
    period = models.CharField(max_length=7, db_index=True)
    previous_value = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    consumption = models.DecimalField(max_digits=12, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.subscriber} - {self.period} - {self.amount}"