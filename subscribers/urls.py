from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceTypeViewSet, SubscriberViewSet, MeterViewSet

router = DefaultRouter()
router.register('services', ServiceTypeViewSet, basename='services')
router.register('subscribers', SubscriberViewSet, basename='subscribers')
router.register('meters', MeterViewSet, basename='meters')

urlpatterns = [
    path('', include(router.urls)),
]