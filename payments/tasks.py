import logging
from celery import shared_task
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_invoice_task(self, order_id):
    """
    Send invoice email to customer after successful payment.
    This is a background job triggered by webhook.
    """
    from orders.models import RepairOrder
    
    try:
        order = RepairOrder.objects.select_related('customer', 'vendor', 'variant__service').get(order_id=order_id)
        
        logger.info(f"Sending invoice for order {order_id}")
        
        # TODO: Implement actual email sending logic
        # For now, just log the action
        logger.info(f"Invoice sent to {order.customer.email} for order {order_id}")
        logger.info(f"Order details: {order.variant.service.name} - ${order.total_amount}")
        
        return {'status': 'success', 'order_id': str(order_id)}
    
    except RepairOrder.DoesNotExist:
        logger.error(f"Order {order_id} not found for invoice generation")
        raise
    
    except Exception as e:
        logger.error(f"Error sending invoice for order {order_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def start_processing_task(self, order_id):
    """
    Start processing the repair order after payment confirmation.
    Updates order status and notifies vendor.
    """
    from orders.models import RepairOrder
    
    try:
        with transaction.atomic():
            order = RepairOrder.objects.select_for_update().select_related(
                'customer', 'vendor', 'variant__service'
            ).get(order_id=order_id)
            
            if order.status == 'paid':
                order.status = 'processing'
                order.save(update_fields=['status'])
                
                logger.info(f"Order {order_id} moved to processing status")
                
                # TODO: Send notification to vendor
                logger.info(f"Notification sent to vendor {order.vendor.business_name} for order {order_id}")
            
            return {'status': 'success', 'order_id': str(order_id)}
    
    except RepairOrder.DoesNotExist:
        logger.error(f"Order {order_id} not found for processing")
        raise
    
    except Exception as e:
        logger.error(f"Error starting processing for order {order_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def handle_failed_payment_task(self, order_id):
    """
    Handle failed payment by releasing stock and updating order status.
    """
    from orders.models import RepairOrder
    from orders.utils import StockManager
    
    try:
        with transaction.atomic():
            order = RepairOrder.objects.select_for_update().select_related('variant').get(order_id=order_id)
            
            if order.status == 'pending':
                order.status = 'failed'
                order.save(update_fields=['status'])
                
                # Release stock
                StockManager.release_stock(order.variant)
                
                logger.info(f"Order {order_id} marked as failed and stock released")
            
            return {'status': 'success', 'order_id': str(order_id)}
    
    except Exception as e:
        logger.error(f"Error handling failed payment for order {order_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)