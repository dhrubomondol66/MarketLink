import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    def test_register_customer_success(self, api_client):
        data = {
            'email': 'newcustomer@test.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'customer'
        }
        
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['user']['email'] == data['email']
        assert response.data['user']['role'] == 'customer'
    
    def test_register_vendor_success(self, api_client):
        data = {
            'email': 'newvendor@test.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'role': 'vendor'
        }
        
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['role'] == 'vendor'
    
    def test_register_password_mismatch(self, api_client):
        data = {
            'email': 'test@test.com',
            'password': 'securepass123',
            'password_confirm': 'different123',
            'role': 'customer'
        }
        
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_invalid_role(self, api_client):
        data = {
            'email': 'test@test.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'role': 'admin'
        }
        
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_duplicate_email(self, api_client, customer_user):
        data = {
            'email': customer_user.email,
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'role': 'customer'
        }
        
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    def test_login_success(self, api_client, customer_user):
        data = {
            'email': 'customer@test.com',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/login/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'user' in response.data
    
    def test_login_invalid_credentials(self, api_client, customer_user):
        data = {
            'email': 'customer@test.com',
            'password': 'wrongpassword'
        }
        
        response = api_client.post('/api/auth/login/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_inactive_user(self, api_client, customer_user):
        customer_user.is_active = False
        customer_user.save()
        
        data = {
            'email': 'customer@test.com',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/login/', data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN