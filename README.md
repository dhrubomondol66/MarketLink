# MarketLink - Multi-Vendor Marketplace for Vehicle Repair Services

A comprehensive Django REST Framework-based API for a multi-vendor marketplace platform specializing in vehicle repair services. Features real-time order management, payment processing, and vendor management.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## ✨ Features

- **Multi-Vendor Support**: Multiple vendors can register and manage their services
- **Service Management**: Vendors can create and manage vehicle repair services with variants
- **Order Management**: Customers can place orders with real-time stock management
- **Payment Processing**: Integrated Stripe payment processing with webhook handling
- **JWT Authentication**: Secure token-based authentication
- **Real-time Updates**: Celery task queue for asynchronous operations
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Distributed Locking**: Redis-based stock management with distributed locks

## 🛠 Technology Stack

- **Backend**: Django 4.2.9, Django REST Framework 3.14.0
- **Database**: PostgreSQL 15
- **Cache & Message Queue**: Redis 7
- **Task Queue**: Celery 5.3.4
- **Payment**: Stripe 7.8.0
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Testing**: pytest, pytest-django, pytest-cov
- **Containerization**: Docker, Docker Compose

## 🚀 Installation

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Option 1: Local Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd MarketLink
```

2. **Create and activate virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirments.txt
```

4. **Create `.env` file**

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run migrations**

```bash
python manage.py migrate
```

6. **Create superuser**

```bash
python manage.py createsuperuser
```

7. **Run development server**

```bash
python manage.py runserver
```

### Option 2: Docker Installation

1. **Build and run with Docker Compose**

```bash
docker-compose up -d
```

2. **Run migrations in Docker**

```bash
docker-compose exec web python manage.py migrate
```

3. **Create superuser in Docker**

```bash
docker-compose exec web python manage.py createsuperuser
```

The application will be available at `http://localhost:8000`

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/marketlink

# Redis
REDIS_URL=redis://localhost:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# JWT Tokens
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 🏃 Running the Project

### Development Server

```bash
python manage.py runserver
```

### Celery Worker

```bash
celery -A MarketLink worker -l info
```

### Celery Beat (Scheduled Tasks)

```bash
celery -A MarketLink beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### With Docker

```bash
docker-compose up
docker-compose down  # Stop all services
```

## 📚 API Documentation

### Swagger UI

Visit `http://localhost:8000/api/docs/` for interactive API documentation

### ReDoc

Visit `http://localhost:8000/api/redoc/` for alternative documentation

## 🧪 Testing

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=.
```

### Run specific test file

```bash
pytest apps/users/tests.py -v
```

### Run specific test class

```bash
pytest apps/orders/tests/test_concurrency.py::OrderConcurrencyTest -v
```

## 📁 Project Structure

```
MarketLink/
├── MarketLink/              # Project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL configuration
│   ├── wsgi.py              # WSGI application
│   ├── celery.py            # Celery configuration
│   └── asgi.py              # ASGI application
│
├── core/                    # Core utilities
│   ├── exceptions.py        # Custom exceptions
│   ├── permissions.py       # Custom permissions
│   └── models.py            # Base models
│
├── users/                   # User management
│   ├── models.py            # User model
│   ├── views.py             # User views
│   ├── serializers.py       # User serializers
│   ├── urls.py              # User URLs
│   └── tests/               # User tests
│
├── vendors/                 # Vendor management
│   ├── models.py            # Vendor model
│   ├── views.py             # Vendor views
│   ├── serializers.py       # Vendor serializers
│   ├── permissions.py       # Vendor permissions
│   ├── urls.py              # Vendor URLs
│   └── tests/               # Vendor tests
│
├── services/                # Service management
│   ├── models.py            # Service models
│   ├── views.py             # Service views
│   ├── serializers.py       # Service serializers
│   ├── permissions.py       # Service permissions
│   ├── urls.py              # Service URLs
│   └── tests/               # Service tests
│
├── orders/                  # Order management
│   ├── models.py            # Order models
│   ├── views.py             # Order views
│   ├── serializers.py       # Order serializers
│   ├── permissions.py       # Order permissions
│   ├── urls.py              # Order URLs
│   ├── utils.py             # Order utilities (StockManager)
│   └── tests/               # Order tests
│
├── payments/                # Payment processing
│   ├── models.py            # Payment models
│   ├── views.py             # Payment views
│   ├── tasks.py             # Celery tasks
│   ├── urls.py              # Payment URLs
│   └── tests/               # Payment tests
│
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── pytest.ini               # Pytest configuration
├── docker-compose.yml       # Docker services
├── Dockerfile               # Docker image
└── README.md                # This file
```

## 👥 User Roles

- **Customer**: Can browse services, place orders, and make payments
- **Vendor**: Can manage services, variants, and view orders
- **Admin**: Full system access and management

## 🔒 Security Features

- JWT token-based authentication
- CORS protection
- CSRF protection
- Password hashing with Django's default algorithm
- Secure Stripe webhook handling
- Role-based access control
- Rate limiting (configurable)

## 📊 Database Models

### Users

- Custom user model with email as username
- Role-based access (customer, vendor, admin)
- JWT token support with blacklisting

### Vendors

- Vendor profile with business information
- Business verification status
- Service management capabilities

### Services

- Service catalog per vendor
- Multiple variants per service (e.g., different vehicle types)
- Stock management with distributed locking
- Pricing and description

### Orders

- Order creation and management
- Status tracking (pending, paid, processing, completed, failed)
- Item-level order details
- Timestamp tracking

### Payments

- Stripe payment integration
- Webhook event processing
- Payment status tracking
- Invoice generation

## 🔧 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
psql --version
# Update DATABASE_URL in .env
```

### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping  # Should return PONG
```

### Missing Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Import Errors

```bash
# Ensure all packages are installed
pip install -r requirments.txt
# Check Python path
python -c "import django; print(django.get_version())"
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues, questions, or suggestions, please open an issue in the repository or contact the development team.

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Real-time notifications (WebSockets)
- [ ] Advanced analytics dashboard
- [ ] Service provider ratings and reviews
- [ ] Scheduled maintenance tracking
- [ ] Multi-language support
- [ ] Integration with popular payment gateways
- [ ] AI-powered service recommendations
___________
