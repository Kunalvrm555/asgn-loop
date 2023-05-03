from rest_framework import serializers
from .models import Store, StoreStatus, BusinessHours


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class StoreStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreStatus
        fields = '__all__'


class BusinessHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHours
        fields = '__all__'


class ReportSerializer(serializers.Serializer):
    store_id = serializers.CharField(max_length=100)
    uptime_last_hour = serializers.FloatField()
    uptime_last_day = serializers.FloatField()
    uptime_last_week = serializers.FloatField()
    downtime_last_hour = serializers.FloatField()
    downtime_last_day = serializers.FloatField()
    downtime_last_week = serializers.FloatField()
