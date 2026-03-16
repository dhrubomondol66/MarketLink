from django.contrib import admin
from .models import Service, ServiceVariant


class ServiceVariantInline(admin.TabularInline):
    model = ServiceVariant
    extra = 1
    fields = ('name', 'price', 'estimated_minutes', 'stock', 'description')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'vendor__business_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ServiceVariantInline]
    
    fieldsets = (
        ('Service Information', {
            'fields': ('vendor', 'name', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceVariant)
class ServiceVariantAdmin(admin.ModelAdmin):
    list_display = ('service', 'name', 'price', 'stock', 'estimated_minutes')
    list_filter = ('name', 'service__vendor')
    search_fields = ('service__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Variant Information', {
            'fields': ('service', 'name', 'price', 'estimated_minutes', 'stock', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )