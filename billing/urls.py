from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TariffViewSet, ReadingViewSet, InvoiceViewSet,
    DebtorsReportView, MonthlyReportView
)

router = DefaultRouter()
router.register('tariffs', TariffViewSet, basename='tariffs')
router.register('readings', ReadingViewSet, basename='readings')
router.register('invoices', InvoiceViewSet, basename='invoices')

urlpatterns = [
    path('reports/debtors/', DebtorsReportView.as_view(), name='debtors-report'),
    path('reports/monthly/', MonthlyReportView.as_view(), name='monthly-report'),
    path('', include(router.urls)),
]