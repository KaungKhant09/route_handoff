from django.contrib import admin
from .models import PickUpLocation, DropOffLocation, NavigationSession


@admin.register(PickUpLocation)
class PickUpLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']


@admin.register(DropOffLocation)
class DropOffLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']


@admin.register(NavigationSession)
class NavigationSessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'pickup', 'dropoff', 'state', 'created_at', 'updated_at']
    list_filter = ['state', 'created_at']
    search_fields = ['session_key']
    readonly_fields = ['created_at', 'updated_at']
