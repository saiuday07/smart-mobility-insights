from django.contrib.auth.models import User
from django.db import models


class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    origin_name = models.CharField(max_length=255)
    dest_name = models.CharField(max_length=255)
    origin_lat = models.FloatField()
    origin_lng = models.FloatField()
    dest_lat = models.FloatField()
    dest_lng = models.FloatField()
    distance_km = models.FloatField()
    duration_sec = models.FloatField()
    route_geometry = models.JSONField()
    vehicle_type = models.CharField(max_length=50, default='car')
    toll_amount = models.FloatField(null=True, blank=True)
    pricing_model = models.CharField(max_length=20, null=True, blank=True)
    congestion_level = models.CharField(max_length=20, default='light')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.origin_name} → {self.dest_name} ({self.vehicle_type})"


class TollCollection(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='toll')
    base_toll = models.FloatField()
    multiplier = models.FloatField()
    total_toll = models.FloatField()
    pricing_model = models.CharField(max_length=20)

    def __str__(self):
        return f"₹{self.total_toll} - {self.trip}"


class CongestionLog(models.Model):
    location_name = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()
    level = models.FloatField(default=1.0)
    source = models.CharField(max_length=50, default='query')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location_name} ({self.level})"
