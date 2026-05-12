from django.contrib import admin
from .models import Trip, TollCollection, CongestionLog


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['user', 'origin_name', 'dest_name', 'distance_km', 'toll_amount', 'vehicle_type', 'created_at']
    list_filter = ['vehicle_type', 'congestion_level', 'created_at']
    search_fields = ['origin_name', 'dest_name', 'user__username']
    date_hierarchy = 'created_at'


@admin.register(TollCollection)
class TollCollectionAdmin(admin.ModelAdmin):
    list_display = ['trip', 'base_toll', 'multiplier', 'total_toll', 'pricing_model']
    list_filter = ['pricing_model']


@admin.register(CongestionLog)
class CongestionLogAdmin(admin.ModelAdmin):
    list_display = ['location_name', 'level', 'source', 'created_at']
    list_filter = ['source', 'created_at']
