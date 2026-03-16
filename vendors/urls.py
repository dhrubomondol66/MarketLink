from django.urls import path
from .views import VendorProfileListCreateView, VendorProfileDetailView

urlpatterns = [
    path('', VendorProfileListCreateView.as_view(), name='vendor-list-create'),
    path('<uuid:id>/', VendorProfileDetailView.as_view(), name='vendor-detail'),
]