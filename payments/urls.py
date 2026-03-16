from django.urls import path
from .views import StripeWebhookView

urlpatterns = [
    path('payment/', StripeWebhookView.as_view(), name='stripe-webhook'),
]