from django.contrib import admin
from .models import ServiceType, Subscriber, Meter


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'full_name', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('account_number', 'full_name', 'address')


@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'subscriber', 'service', 'installed_at', 'is_active')
    list_filter = ('service', 'is_active')
    search_fields = ('serial_number', 'subscriber__full_name')