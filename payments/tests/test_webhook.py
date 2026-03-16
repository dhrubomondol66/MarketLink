import pytest
import json
from unittest.mock import patch, MagicMock
from django.urls import reverse
from orders.models import RepairOrder
from payments.models import ProcessedWebhookEvent


@pytest.mark.django_db
class TestWebhookIdempotency:
    """Test webhook idempotency handling"""
    
    @patch('stripe.Webhook.construct_event')
    def test_duplicate_webhook_ignored(self, mock_construct, api_client, customer_user, service_variant):
        """Test that duplicate webhook events are ignored"""
        # Create an order
        order = RepairOrder.objects.create(
            customer=customer_user,
            vendor=service_variant.service.vendor,
            variant=service_variant,
            total_amount=service_variant.price,
            status='pending',
            stripe_session_id='cs_test_123'
        )
        
        # Mock Stripe event
        mock_event = MagicMock()
        mock_event.id = 'evt_test_123'
        mock_event.type = 'checkout.session.completed'
        mock_event.data.object.metadata = {'order_id': str(order.order_id)}
        mock_event.data.object.amount_total = int(service_variant.price * 100)
        mock_event.data.object.payment_intent = 'pi_test_123'
        mock_construct.return_value = mock_event
        
        url = reverse('stripe-webhook')
        
        # First webhook call
        response1 = api_client.post(
            url,
            data=json.dumps({'type': 'checkout.session.completed'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        assert response1.status_code == 200
        order.refresh_from_db()
        assert order.status == 'paid'
        
        # Reset order status to test idempotency
        order.status = 'paid'
        order.save()
        
        # Second webhook call (duplicate)
        response2 = api_client.post(
            url,
            data=json.dumps({'type': 'checkout.session.completed'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        assert response2.status_code == 200
        assert response2.data['status'] == 'already_processed'
        
        # Verify event only recorded once
        assert ProcessedWebhookEvent.objects.filter(event_id='evt_test_123').count() == 1
    
    @patch('stripe.Webhook.construct_event')
    def test_amount_mismatch_fails(self, mock_construct, api_client, customer_user, service_variant):
        """Test that amount mismatch causes failure"""
        order = RepairOrder.objects.create(
            customer=customer_user,
            vendor=service_variant.service.vendor,
            variant=service_variant,
            total_amount=service_variant.price,
            status='pending',
            stripe_session_id='cs_test_456'
        )
        
        # Mock event with wrong amount
        mock_event = MagicMock()
        mock_event.id = 'evt_test_456'
        mock_event.type = 'checkout.session.completed'
        mock_event.data.object.metadata = {'order_id': str(order.order_id)}
        mock_event.data.object.amount_total = int(service_variant.price * 100) + 1000  # Wrong amount
        mock_event.data.object.payment_intent = 'pi_test_456'
        mock_construct.return_value = mock_event
        
        url = reverse('stripe-webhook')
        
        response = api_client.post(
            url,
            data=json.dumps({'type': 'checkout.session.completed'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == 'failed'
    
    def test_invalid_signature_rejected(self, api_client):
        """Test that invalid signature is rejected"""
        url = reverse('stripe-webhook')
        
        response = api_client.post(
            url,
            data=json.dumps({'type': 'checkout.session.completed'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='invalid_signature'
        )
        
        assert response.status_code == 400
    
    def test_missing_signature_rejected(self, api_client):
        """Test that missing signature is rejected"""
        url = reverse('stripe-webhook')
        
        response = api_client.post(
            url,
            data=json.dumps({'type': 'checkout.session.completed'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400


@pytest.mark.django_db
class TestWebhookEventHandling:
    """Test different webhook event types"""
    
    @patch('stripe.Webhook.construct_event')
    @patch('payments.tasks.send_invoice_task.delay')
    @patch('payments.tasks.start_processing_task.delay')
    def test_checkout_completed_triggers_tasks(
        self, mock_processing, mock_invoice, mock_construct, 
        api_client, customer_user, service_variant
    ):
        """Test that successful checkout triggers background tasks"""
        order = RepairOrder.objects.create(
            customer=customer_user,
            vendor=service_variant.service.vendor,
            variant=service_variant,
            total_amount=service_variant.price,
            status='pending'
        )
        
        mock_event = MagicMock()
        mock_event.id = 'evt_test_789'
        mock_event.type = 'checkout.session.completed'
        mock_event.data.object.metadata = {'order_id': str(order.order_id)}
        mock_event.data.object.amount_total = int(service_variant.price * 100)
        mock_event.data.object.payment_intent = 'pi_test_789'
        mock_construct.return_value = mock_event
        
        url = reverse('stripe-webhook')
        
        response = api_client.post(
            url,
            data=json.dumps({'type': 'checkout.session.completed'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        assert response.status_code == 200
        
        # Verify tasks were called
        mock_invoice.assert_called_once()
        mock_processing.assert_called_once()
    
    @patch('stripe.Webhook.construct_event')
    @patch('payments.tasks.handle_failed_payment_task.delay')
    def test_checkout_expired_triggers_failure(
        self, mock_failed, mock_construct, 
        api_client, customer_user, service_variant
    ):
        """Test that expired checkout triggers failure handling"""
        order = RepairOrder.objects.create(
            customer=customer_user,
            vendor=service_variant.service.vendor,
            variant=service_variant,
            total_amount=service_variant.price,
            status='pending'
        )
        
        mock_event = MagicMock()
        mock_event.id = 'evt_test_expired'
        mock_event.type = 'checkout.session.expired'
        mock_event.data.object.metadata = {'order_id': str(order.order_id)}
        mock_construct.return_value = mock_event
        
        url = reverse('stripe-webhook')
        
        response = api_client.post(
            url,
            data=json.dumps({'type': 'checkout.session.expired'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        assert response.status_code == 200
        mock_failed.assert_called_once()