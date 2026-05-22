from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Service, ServiceVariant
from .serializers import ServiceSerializer, ServiceVariantSerializer, ServiceVariantCreateSerializer
from vendors.permissions import IsVendor, IsVendorOwner


class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsVendor()]
    
    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True).select_related('vendor__user').prefetch_related('variants')
        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)
        return queryset


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceSerializer
    lookup_field = 'id'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsVendor()]
    
    def get_queryset(self):
        if self.request.method == 'GET':
            return Service.objects.filter(is_active=True).select_related('vendor__user').prefetch_related('variants')
        if not self.request.user.is_authenticated:
            return Service.objects.none()
        return Service.objects.filter(vendor__user=self.request.user).select_related('vendor__user').prefetch_related('variants')


class ServiceVariantCreateView(generics.CreateAPIView):
    serializer_class = ServiceVariantCreateSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    
    def create(self, request, *args, **kwargs):
        service_id = self.kwargs.get('service_id')
        service = get_object_or_404(Service, id=service_id, vendor__user=request.user)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant = serializer.save(service=service)
        
        response_serializer = ServiceVariantSerializer(variant)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ServiceVariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceVariantSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    lookup_field = 'id'
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ServiceVariant.objects.none()
        return ServiceVariant.objects.filter(service__vendor__user=self.request.user)