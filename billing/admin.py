from django.contrib import admin
from .models import Tariff, Reading, Invoice


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('service', 'price_per_unit', 'valid_from', 'valid_to')
    list_filter = ('service',)
    search_fields = ('service__name',)


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ('meter', 'period', 'value', 'status', 'submitted_by', 'created_at')
    list_filter = ('status', 'period')
    search_fields = ('meter__serial_number', 'meter__subscriber__full_name')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'period', 'amount', 'is_paid', 'paid_at')
    list_filter = ('is_paid', 'period')
    search_fields = ('subscriber__full_name', 'subscriber__account_number')