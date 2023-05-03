from django.db import models

class Store(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    timezone_str = models.CharField(max_length=100, default="America/Chicago")

class StoreStatus(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)

class BusinessHours(models.Model):
    WEEKDAYS = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    day_of_week = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()
