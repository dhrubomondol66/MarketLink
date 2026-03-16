import logging
import stripe
from django.conf import settings
from django.db import transaction
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import RepairOrder
from .serializers import (
    RepairOrderSerializer,
    RepairOrderCreateSerializer,
    RepairOrderDetailSerializer
)
from .utils import StockManager
from services.models import ServiceVariant

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class RepairOrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RepairOrderCreateSerializer
        return RepairOrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = RepairOrder.objects.select_related(
            'customer', 'vendor__user', 'variant__service'
        )
        
        if user.role == 'vendor' and hasattr(user, 'vendor_profile'):
            return queryset.filter(vendor=user.vendor_profile)
        
        return queryset.filter(customer=user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        variant_id = serializer.validated_data['service_variant']
        variant = ServiceVariant.objects.select_related('service__vendor').get(id=variant_id)
        
        with transaction.atomic():
            # Create order first
            order = RepairOrder.objects.create(
                customer=request.user,
                vendor=variant.service.vendor,
                variant=variant,
                total_amount=variant.price,
                notes=serializer.validated_data.get('notes', ''),
                status='pending'
            )
            
            # Reserve stock with concurrency protection
            try:
                StockManager.reserve_stock(variant, order)
            except Exception as e:
                # If stock reservation fails, delete the order
                order.delete()
                raise
            
            # Create Stripe checkout session
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(variant.price * 100),
                            'product_data': {
                                'name': f"{variant.service.name} - {variant.get_name_display()}",
                                'description': variant.description or variant.service.description,
                            },
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=settings.PAYMENT_SUCCESS_URL + f'?order_id={order.order_id}',
                    cancel_url=settings.PAYMENT_CANCEL_URL + f'?order_id={order.order_id}',
                    metadata={
                        'order_id': str(order.order_id),
                    }
                )
                
                order.stripe_session_id = checkout_session.id
                order.save(update_fields=['stripe_session_id'])
                
                response_data = RepairOrderCreateSerializer(order).data
                response_data['payment_url'] = checkout_session.url
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error creating checkout session for order {order.order_id}: {str(e)}")
                
                # Release stock and mark order as failed
                StockManager.release_stock(variant)
                order.status = 'failed'
                order.save(update_fields=['status'])
                
                return Response(
                    {'error': 'Failed to create payment session'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class RepairOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RepairOrderDetailSerializer
    lookup_field = 'order_id'
    
    def get_queryset(self):
        user = self.request.user
        queryset = RepairOrder.objects.select_related(
            'customer', 'vendor__user', 'variant__service'
        )
        
        if user.role == 'vendor' and hasattr(user, 'vendor_profile'):
            return queryset.filter(vendor=user.vendor_profile)
        
        return queryset.filter(customer=user)


class RepairOrderCancelView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_id):
        try:
            order = RepairOrder.objects.select_related('variant').get(
                order_id=order_id,
                customer=request.user
            )
        except RepairOrder.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not order.can_be_cancelled():
            return Response(
                {'error': f'Order cannot be cancelled in {order.status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            order.status = 'cancelled'
            order.save(update_fields=['status'])
            
            # Release stock back
            StockManager.release_stock(order.variant)
        
        return Response(
            {'message': 'Order cancelled successfully'},
            status=status.HTTP_200_OK
        )