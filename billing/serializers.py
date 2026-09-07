from rest_framework import serializers
from django.db import models
from .models import Tariff, Reading, Invoice


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'

    def create(self, validated_data):
        service = validated_data['service']
        valid_from = validated_data['valid_from']

        Tariff.objects.filter(service=service, valid_to__isnull=True).update(
            valid_to=valid_from
        )

        return Tariff.objects.create(**validated_data)


class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reading
        fields = '__all__'
        read_only_fields = ['status', 'reject_reason', 'submitted_by', 'reviewed_by']

    def validate(self, data):
        meter = data['meter']
        value = data['value']

        last_reading = Reading.objects.filter(
            meter=meter, status='tasdiqlangan'
        ).order_by('-period').first()

        if last_reading:
            if value < last_reading.value:
                raise serializers.ValidationError(
                    'Yangi ko\'rsatkich oldingisidan kichik bo\'lishi mumkin emas'
                )
        else:
            if value < meter.initial_value:
                raise serializers.ValidationError(
                    'Ko\'rsatkich boshlang\'ich qiymatdan kichik bo\'lishi mumkin emas'
                )

        return data


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'