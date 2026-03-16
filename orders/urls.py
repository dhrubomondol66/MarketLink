from django.urls import path
from .views import (
    RepairOrderListCreateView,
    RepairOrderDetailView,
    RepairOrderCancelView
)

urlpatterns = [
    path('', RepairOrderListCreateView.as_view(), name='order-list-create'),
    path('<uuid:order_id>/', RepairOrderDetailView.as_view(), name='order-detail'),
    path('<uuid:order_id>/cancel/', RepairOrderCancelView.as_view(), name='order-cancel'),
]