from django.contrib import admin
from .models import RepairOrder


@admin.register(RepairOrder)
class RepairOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'vendor', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'customer__email', 'vendor__business_name')
    readonly_fields = ('order_id', 'created_at', 'updated_at', 'stripe_session_id', 'stripe_payment_intent_id')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'customer', 'vendor', 'variant', 'status', 'total_amount', 'notes')
        }),
        ('Payment Information', {
            'fields': ('stripe_session_id', 'stripe_payment_intent_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False