from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import Tariff, Reading, Invoice
from .serializers import TariffSerializer, ReadingSerializer, InvoiceSerializer
from .permissions import IsAdmin, IsNazoratchiOrAdmin, IsAbonent


class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['service']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Tariflar tarixi',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'message': 'Yangi tarif kiritildi',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class ReadingViewSet(viewsets.ModelViewSet):
    queryset = Reading.objects.all()
    serializer_class = ReadingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['period', 'status', 'meter__service']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Ko\'rsatkichlar ro\'yxati',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(submitted_by=request.user)
        return Response({
            'success': True,
            'message': 'Ko\'rsatkich yuborildi',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my')
    def my_readings(self, request):
        subscriber = getattr(request.user, 'subscriber', None)
        if not subscriber:
            return Response({
                'success': False,
                'message': 'Sizga bog\'langan abonent topilmadi',
                'data': []
            })

        readings = Reading.objects.filter(meter__subscriber=subscriber)
        serializer = self.get_serializer(readings, many=True)
        return Response({
            'success': True,
            'message': 'Mening ko\'rsatkichlarim',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        reading = self.get_object()

        if reading.status == 'tasdiqlangan':
            return Response({
                'success': False,
                'message': 'Bu ko\'rsatkich allaqachon tasdiqlangan'
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            meter = reading.meter

            last_invoice = Invoice.objects.filter(
                reading__meter=meter
            ).order_by('-period').first()

            previous_value = last_invoice.current_value if last_invoice else meter.initial_value
            consumption = reading.value - previous_value

            year, month = reading.period.split('-')
            period_start = f"{year}-{month}-01"

            tariff = Tariff.objects.filter(
                service=meter.service,
                valid_from__lte=period_start
            ).filter(
                Q(valid_to__isnull=True) | Q(valid_to__gte=period_start)
            ).order_by('-valid_from').first()

            if not tariff:
                return Response({
                    'success': False,
                    'message': 'Bu davr uchun tarif topilmadi'
                }, status=status.HTTP_400_BAD_REQUEST)

            amount = consumption * tariff.price_per_unit

            reading.status = 'tasdiqlangan'
            reading.reviewed_by = request.user
            reading.save()

            invoice = Invoice.objects.create(
                reading=reading,
                subscriber=meter.subscriber,
                period=reading.period,
                previous_value=previous_value,
                current_value=reading.value,
                consumption=consumption,
                price_per_unit=tariff.price_per_unit,
                amount=amount
            )

        return Response({
            'success': True,
            'message': 'Ko\'rsatkich tasdiqlandi, hisob chiqarildi',
            'data': InvoiceSerializer(invoice).data
        })

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        reading = self.get_object()
        reason = request.data.get('reject_reason', '')

        reading.status = 'rad_etilgan'
        reading.reject_reason = reason
        reading.reviewed_by = request.user
        reading.save()

        return Response({
            'success': True,
            'message': 'Ko\'rsatkich rad etildi',
            'data': self.get_serializer(reading).data
        })


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['period', 'is_paid', 'subscriber']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Hisoblar ro\'yxati',
            'data': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='my')
    def my_invoices(self, request):
        subscriber = getattr(request.user, 'subscriber', None)
        if not subscriber:
            return Response({
                'success': False,
                'message': 'Sizga bog\'langan abonent topilmadi',
                'data': []
            })

        invoices = Invoice.objects.filter(subscriber=subscriber).order_by('-period')[:6]
        debt = Invoice.objects.filter(subscriber=subscriber, is_paid=False).aggregate(
            total=Sum('amount')
        )['total'] or 0

        serializer = self.get_serializer(invoices, many=True)
        return Response({
            'success': True,
            'message': 'Mening hisoblarim',
            'data': {
                'invoices': serializer.data,
                'total_debt': debt
            }
        })

    @action(detail=True, methods=['post'], url_path='pay')
    def pay(self, request, pk=None):
        invoice = self.get_object()
        invoice.is_paid = True
        invoice.paid_at = timezone.now()
        invoice.save()

        return Response({
            'success': True,
            'message': 'To\'lov qayd etildi',
            'data': self.get_serializer(invoice).data
        })


class DebtorsReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        debtors = Invoice.objects.filter(is_paid=False).values(
            'subscriber__id', 'subscriber__full_name', 'subscriber__account_number'
        ).annotate(
            months_count=Count('id'),
            total_debt=Sum('amount')
        ).order_by('-total_debt')

        return Response({
            'success': True,
            'message': 'Qarzdorlar ro\'yxati',
            'data': list(debtors)
        })


class MonthlyReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        period = request.query_params.get('period')
        if not period:
            return Response({
                'success': False,
                'message': 'period parametri kerak, masalan ?period=2026-08'
            }, status=status.HTTP_400_BAD_REQUEST)

        report = Invoice.objects.filter(period=period).values(
            'reading__meter__service__name'
        ).annotate(
            total_consumption=Sum('consumption'),
            total_amount=Sum('amount')
        )

        return Response({
            'success': True,
            'message': f'{period} oyi bo\'yicha hisobot',
            'data': list(report)
        })