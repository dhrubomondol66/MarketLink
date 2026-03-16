from django.db import models
from django.core.validators import MinValueValidator
from vendors.models import VendorProfile
import uuid


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name='services'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        indexes = [
            models.Index(fields=['vendor', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.vendor.business_name}"


class ServiceVariant(models.Model):
    VARIANT_TYPES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('express', 'Express'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    name = models.CharField(max_length=50, choices=VARIANT_TYPES)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    estimated_minutes = models.PositiveIntegerField(
        help_text="Estimated time in minutes"
    )
    stock = models.PositiveIntegerField(
        default=1,
        help_text="Number of simultaneous bookings that can be accepted"
    )
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_variants'
        verbose_name = 'Service Variant'
        verbose_name_plural = 'Service Variants'
        unique_together = [['service', 'name']]
        indexes = [
            models.Index(fields=['service']),
            models.Index(fields=['stock']),
        ]
    
    def __str__(self):
        return f"{self.service.name} - {self.get_name_display()}"
    
    def has_stock(self):
        return self.stock > 0