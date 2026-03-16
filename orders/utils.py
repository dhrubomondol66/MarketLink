import redis
import logging
import time
from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

# Try to connect to Redis, fallback to None if unavailable
try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
    logger.info("Redis connection established for stock locking")
except (redis.exceptions.ConnectionError, redis.exceptions.RedisError):
    redis_client = None
    REDIS_AVAILABLE = False
    logger.warning("Redis unavailable - using database-only locking for stock management")


class StockManager:
    """Handles concurrency-safe stock management using Redis locks (with DB-only fallback)"""
    
    @staticmethod
    def acquire_lock(variant_id, timeout=None):
        """Acquire a distributed lock for a service variant"""
        if not REDIS_AVAILABLE:
            return None
            
        if timeout is None:
            timeout = settings.REDIS_LOCK_TIMEOUT
        
        lock_key = f"service_variant_lock:{variant_id}"
        lock = redis_client.lock(lock_key, timeout=timeout, blocking_timeout=timeout)
        return lock
    
    @staticmethod
    def reserve_stock(variant, order):
        """
        Reserve stock for an order with concurrency protection.
        Uses Redis distributed lock + database-level locking when Redis is available.
        Falls back to database-only locking when Redis is unavailable.
        """
        from services.models import ServiceVariant
        
        # Fallback: Database-only locking (no Redis)
        if not REDIS_AVAILABLE:
            with transaction.atomic():
                variant = ServiceVariant.objects.select_for_update().get(id=variant.id)
                
                if variant.stock < 1:
                    raise ValidationError({
                        'variant': 'No stock available for this service variant'
                    })
                
                variant.stock -= 1
                variant.save(update_fields=['stock'])
                
                logger.info(f"Stock reserved for order {order.order_id}, variant {variant.id}, remaining stock: {variant.stock}")
                return variant
        
        # Full Redis + DB locking
        max_attempts = settings.STOCK_LOCK_RETRY_ATTEMPTS
        attempt = 0
        
        while attempt < max_attempts:
            try:
                lock = StockManager.acquire_lock(variant.id)
                
                if lock.acquire(blocking=False):
                    try:
                        with transaction.atomic():
                            # Refresh from database with row-level lock
                            variant = ServiceVariant.objects.select_for_update().get(id=variant.id)
                            
                            if variant.stock < 1:
                                raise ValidationError({
                                    'variant': 'No stock available for this service variant'
                                })
                            
                            # Decrement stock atomically
                            variant.stock -= 1
                            variant.save(update_fields=['stock'])
                            
                            logger.info(f"Stock reserved for order {order.order_id}, variant {variant.id}, remaining stock: {variant.stock}")
                            return variant
                    finally:
                        lock.release()
                else:
                    # Lock acquisition failed, retry with exponential backoff
                    attempt += 1
                    if attempt < max_attempts:
                        wait_time = 0.1 * (2 ** attempt)
                        logger.warning(f"Failed to acquire lock for variant {variant.id}, attempt {attempt}/{max_attempts}, retrying in {wait_time}s")
                        time.sleep(wait_time)
                    else:
                        raise ValidationError({
                            'variant': 'Service is currently busy, please try again'
                        })
            
            except redis.exceptions.LockError as e:
                logger.error(f"Redis lock error for variant {variant.id}: {str(e)}")
                raise ValidationError({
                    'variant': 'Unable to process booking at this time, please try again'
                })
        
        raise ValidationError({
            'variant': 'Failed to reserve stock after multiple attempts'
        })
    
    @staticmethod
    def release_stock(variant):
        """Release stock back when order is cancelled or fails"""
        from services.models import ServiceVariant
        
        # Fallback: Database-only locking (no Redis)
        if not REDIS_AVAILABLE:
            with transaction.atomic():
                variant = ServiceVariant.objects.select_for_update().get(id=variant.id)
                variant.stock += 1
                variant.save(update_fields=['stock'])
                logger.info(f"Stock released for variant {variant.id}, new stock: {variant.stock}")
            return
        
        try:
            lock = StockManager.acquire_lock(variant.id)
            
            if lock.acquire(blocking=True):
                try:
                    with transaction.atomic():
                        variant = ServiceVariant.objects.select_for_update().get(id=variant.id)
                        variant.stock += 1
                        variant.save(update_fields=['stock'])
                        
                        logger.info(f"Stock released for variant {variant.id}, new stock: {variant.stock}")
                finally:
                    lock.release()
        except Exception as e:
            logger.error(f"Error releasing stock for variant {variant.id}: {str(e)}")
            raise