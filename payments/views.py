import logging
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProcessedWebhookEvent
from orders.models import RepairOrder
from .tasks import send_invoice_task, start_processing_task, handle_failed_payment_task
from .services import StripePaymentGateway, PaymentGatewayException

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Handles Stripe webhook events for payment confirmation.
    Implements idempotency to handle duplicate webhook deliveries.
    """
    permission_classes = []
    authentication_classes = []
    
    def post(self, request):
        payload = request.body
        # Use request.headers for more robust retrieval (handles various proxy/server setups)
        sig_header = request.headers.get('Stripe-Signature')
        
        if not sig_header:
            # Fallback to META for older Django versions or specific server configs
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
            
        if not sig_header:
            logger.error(
                f"Missing Stripe signature header. "
                f"Path: {request.path}, "
                f"Method: {request.method}, "
                f"Headers: {dict(request.headers)}"
            )
            return Response(
                {'error': 'Missing signature'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify webhook signature via gateway
            gateway = StripePaymentGateway()
            event = gateway.construct_event(payload, sig_header)
        except PaymentGatewayException as e:
            return Response(
                {'error': str(e)},
                status=e.status_code
            )
        
        # Check if event already processed (idempotency)
        if ProcessedWebhookEvent.objects.filter(event_id=event.id).exists():
            logger.info(f"Event {event.id} already processed, skipping")
            return Response(
                {'status': 'already_processed'},
                status=status.HTTP_200_OK
            )
        
        # Handle the event
        try:
            if event.type == 'checkout.session.completed':
                self.handle_checkout_completed(event)
            elif event.type == 'checkout.session.expired':
                self.handle_checkout_expired(event)
            elif event.type == 'payment_intent.payment_failed':
                self.handle_payment_failed(event)
            else:
                logger.info(f"Unhandled event type: {event.type}")
        
        except Exception as e:
            logger.error(f"Error processing webhook event {event.id}: {str(e)}")
            return Response(
                {'error': 'Processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
    
    def handle_checkout_completed(self, event):
        """Handle successful checkout completion"""
        session = event.data.object
        order_id = session.metadata.get('order_id')
        
        if not order_id:
            logger.error(f"No order_id in session metadata for event {event.id}")
            return
        
        with transaction.atomic():
            # Mark event as processed first (idempotency guarantee)
            ProcessedWebhookEvent.objects.create(
                event_id=event.id,
                event_type=event.type
            )
            
            try:
                order = RepairOrder.objects.select_for_update().get(order_id=order_id)
                
                # If already paid, skip (additional safety check)
                if order.status == 'paid':
                    logger.info(f"Order {order_id} already marked as paid")
                    return
                
                # Verify amount matches
                expected_amount = int(order.total_amount * 100)  # Convert to cents
                actual_amount = session.amount_total
                
                if expected_amount != actual_amount:
                    logger.error(
                        f"Amount mismatch for order {order_id}: "
                        f"expected {expected_amount}, got {actual_amount}"
                    )
                    order.status = 'failed'
                    order.save(update_fields=['status'])
                    return
                
                # Update order status
                order.status = 'paid'
                order.stripe_payment_intent_id = session.payment_intent
                order.save(update_fields=['status', 'stripe_payment_intent_id'])
                
                logger.info(f"Order {order_id} marked as paid")
                
                # Trigger background jobs
                send_invoice_task.delay(str(order_id))
                start_processing_task.delay(str(order_id))
            
            except RepairOrder.DoesNotExist:
                logger.error(f"Order {order_id} not found for event {event.id}")
    
    def handle_checkout_expired(self, event):
        """Handle expired checkout session"""
        session = event.data.object
        order_id = session.metadata.get('order_id')
        
        if not order_id:
            return
        
        with transaction.atomic():
            ProcessedWebhookEvent.objects.create(
                event_id=event.id,
                event_type=event.type
            )
            
            handle_failed_payment_task.delay(str(order_id))
            logger.info(f"Checkout expired for order {order_id}")
    
    def handle_payment_failed(self, event):
        """Handle failed payment"""
        payment_intent = event.data.object
        
        with transaction.atomic():
            ProcessedWebhookEvent.objects.create(
                event_id=event.id,
                event_type=event.type
            )
            
            try:
                order = RepairOrder.objects.select_for_update().get(
                    stripe_payment_intent_id=payment_intent.id
                )
                
                handle_failed_payment_task.delay(str(order.order_id))
                logger.info(f"Payment failed for order {order.order_id}")
            
            except RepairOrder.DoesNotExist:
                logger.warning(f"No order found for payment_intent {payment_intent.id}")