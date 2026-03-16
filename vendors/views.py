from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import VendorProfile
from .serializers import VendorProfileSerializer, VendorProfileCreateSerializer
from .permissions import IsVendor
from rest_framework.permissions import BasePermission

class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "vendor"


class VendorProfileListCreateView(generics.ListCreateAPIView):
    queryset = VendorProfile.objects.filter(is_active=True).select_related('user')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VendorProfileCreateSerializer
        return VendorProfileSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vendor_profile = serializer.save()
        
        response_serializer = VendorProfileSerializer(vendor_profile)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class VendorProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = VendorProfile.objects.select_related('user')
    serializer_class = VendorProfileSerializer
    lookup_field = 'id'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsVendor()]
    
    def get_queryset(self):
        if self.request.method == 'GET':
            return self.queryset.filter(is_active=True)
        return self.queryset.filter(user=self.request.user)