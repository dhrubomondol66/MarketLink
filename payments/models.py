from django.db import models
import uuid


class ProcessedWebhookEvent(models.Model):
    """
    Stores processed webhook events to ensure idempotency.
    Prevents duplicate processing of the same webhook event.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.CharField(max_length=255, unique=True, db_index=True)
    event_type = models.CharField(max_length=100)
    processed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'processed_webhook_events'
        verbose_name = 'Processed Webhook Event'
        verbose_name_plural = 'Processed Webhook Events'
        ordering = ['-processed_at']
        indexes = [
            models.Index(fields=['event_id']),
            models.Index(fields=['processed_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.event_id}"