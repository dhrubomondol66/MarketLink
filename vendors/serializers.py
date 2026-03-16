from rest_framework import serializers
from .models import VendorProfile
from users.serializers import UserSerializer


class VendorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = VendorProfile
        fields = ('id', 'user', 'business_name', 'address', 'phone', 'description', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        user = self.context['request'].user
        if user.role != 'vendor':
            raise serializers.ValidationError("Only users with vendor role can create vendor profiles")
        return attrs


class VendorProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = ('business_name', 'address', 'phone', 'description')
    
    def create(self, validated_data):
        user = self.context['request'].user
        if hasattr(user, 'vendor_profile'):
            raise serializers.ValidationError("Vendor profile already exists for this user")
        
        vendor_profile = VendorProfile.objects.create(user=user, **validated_data)
        return vendor_profile