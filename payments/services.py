import logging
import stripe
from abc import ABC, abstractmethod
from django.conf import settings
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentGatewayException(APIException):
    status_code = 500
    default_detail = 'Payment gateway error'
    default_code = 'payment_gateway_error'

    def __init__(self, detail=None, status_code=None):
        if detail:
            self.detail = detail
        if status_code:
            self.status_code = status_code

class BasePaymentGateway(ABC):
    """
    Abstract base class for all payment gateways.
    Standardizes the interface for creating sessions and handling events.
    """
    
    @abstractmethod
    def create_checkout_session(self, order, success_url, cancel_url):
        pass

    @abstractmethod
    def construct_event(self, payload, sig_header):
        pass

class StripePaymentGateway(BasePaymentGateway):
    """
    Service class to handle Stripe payment operations.
    Acts as the primary interface for Stripe integration.
    """
    
    def create_checkout_session(self, order, success_url, cancel_url):
        """
        Creates a Stripe Checkout Session for a given RepairOrder.
        """
        try:
            variant = order.variant
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(order.total_amount * 100),
                        'product_data': {
                            'name': f"{variant.service.name} - {variant.get_name_display()}",
                            'description': variant.description or variant.service.description,
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url + f'?order_id={order.order_id}',
                cancel_url=cancel_url + f'?order_id={order.order_id}',
                metadata={
                    'order_id': str(order.order_id),
                }
            )
            return checkout_session
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session for order {order.order_id}: {str(e)}")
            raise PaymentGatewayException(detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating checkout session: {str(e)}")
            raise PaymentGatewayException()

    def construct_event(self, payload, sig_header):
        """
        Verifies and constructs a Stripe webhook event.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload for webhook: {str(e)}")
            raise PaymentGatewayException(detail='Invalid payload', status_code=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature for webhook: {str(e)}")
            raise PaymentGatewayException(detail='Invalid signature', status_code=400)
