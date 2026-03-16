import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from vendors.models import VendorProfile
from services.models import Service, ServiceVariant

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer_user(db):
    return User.objects.create_user(
        email='customer@test.com',
        password='testpass123',
        role='customer',
        first_name='John',
        last_name='Doe'
    )


@pytest.fixture
def vendor_user(db):
    return User.objects.create_user(
        email='vendor@test.com',
        password='testpass123',
        role='vendor',
        first_name='Jane',
        last_name='Smith'
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email='admin@test.com',
        password='testpass123'
    )


@pytest.fixture
def vendor_profile(vendor_user):
    return VendorProfile.objects.create(
        user=vendor_user,
        business_name='Auto Repair Shop',
        address='123 Main St, City, State',
        phone='1234567890',
        is_active=True
    )


@pytest.fixture
def service(vendor_profile):
    return Service.objects.create(
        vendor=vendor_profile,
        name='Oil Change',
        description='Professional oil change service',
        is_active=True
    )


@pytest.fixture
def service_variant(service):
    return ServiceVariant.objects.create(
        service=service,
        name='basic',
        price=50.00,
        estimated_minutes=30,
        stock=5
    )


@pytest.fixture
def authenticated_customer(api_client, customer_user):
    api_client.force_authenticate(user=customer_user)
    return api_client


@pytest.fixture
def authenticated_vendor(api_client, vendor_user):
    api_client.force_authenticate(user=vendor_user)
    return api_client