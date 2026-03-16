from django.urls import path
from .views import (
    ServiceListCreateView,
    ServiceDetailView,
    ServiceVariantCreateView,
    ServiceVariantDetailView
)

urlpatterns = [
    path('', ServiceListCreateView.as_view(), name='service-list-create'),
    path('<uuid:id>/', ServiceDetailView.as_view(), name='service-detail'),
    path('<uuid:service_id>/variants/', ServiceVariantCreateView.as_view(), name='variant-create'),
    path('variants/<uuid:id>/', ServiceVariantDetailView.as_view(), name='variant-detail'),
]