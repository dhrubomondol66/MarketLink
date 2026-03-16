from rest_framework import serializers
from .models import Service, ServiceVariant
from vendors.serializers import VendorProfileSerializer


class ServiceVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariant
        fields = ('id', 'name', 'price', 'estimated_minutes', 'stock', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ServiceSerializer(serializers.ModelSerializer):
    vendor = VendorProfileSerializer(read_only=True)
    variants = ServiceVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = ('id', 'vendor', 'name', 'description', 'is_active', 'variants', 'created_at', 'updated_at')
        read_only_fields = ('id', 'vendor', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        user = self.context['request'].user
        if not hasattr(user, 'vendor_profile'):
            raise serializers.ValidationError("You must have a vendor profile to create services")
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        service = Service.objects.create(
            vendor=user.vendor_profile,
            **validated_data
        )
        return service


class ServiceVariantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariant
        fields = ('name', 'price', 'estimated_minutes', 'stock', 'description')
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value