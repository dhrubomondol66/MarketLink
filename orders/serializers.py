from rest_framework import serializers
from .models import RepairOrder
from services.serializers import ServiceVariantSerializer
from vendors.serializers import VendorProfileSerializer
from users.serializers import UserSerializer
#from services.models import ServiceVariant

class RepairOrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    vendor = VendorProfileSerializer(read_only=True)
    variant = ServiceVariantSerializer(read_only=True)
    
    class Meta:
        model = RepairOrder
        fields = (
            'order_id', 'customer', 'vendor', 'variant', 'status',
            'total_amount', 'notes', 'created_at', 'updated_at'
        )
        read_only_fields = ('order_id', 'customer', 'vendor', 'status', 'total_amount', 'created_at', 'updated_at')


class RepairOrderCreateSerializer(serializers.ModelSerializer):
    service_variant = serializers.UUIDField(write_only=True)
    payment_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = RepairOrder
        fields = ('service_variant', 'notes', 'order_id', 'status', 'total_amount', 'payment_url', 'created_at')
        read_only_fields = ('order_id', 'status', 'total_amount', 'payment_url', 'created_at')
    
    def validate_service_variant(self, value):
        from services.models import ServiceVariant
        
        try:
            variant = ServiceVariant.objects.select_related('service__vendor').get(id=value)
        except ServiceVariant.DoesNotExist:
            raise serializers.ValidationError("Service variant not found")
        
        if not variant.service.is_active:
            raise serializers.ValidationError("This service is not currently available")
        
        if not variant.service.vendor.is_active:
            raise serializers.ValidationError("This vendor is not currently active")
        
        return value


class RepairOrderDetailSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    vendor = VendorProfileSerializer(read_only=True)
    variant = ServiceVariantSerializer(read_only=True)
    
    class Meta:
        model = RepairOrder
        fields = (
            'order_id', 'customer', 'vendor', 'variant', 'status',
            'total_amount', 'notes', 'stripe_session_id',
            'created_at', 'updated_at'
        )
        read_only_fields = fields