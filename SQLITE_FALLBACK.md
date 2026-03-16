# SQLite Fallback Configuration for MarketLink

## Use SQLite Temporarily

If you're having issues with PostgreSQL authentication, you can temporarily use SQLite to get the project running, then switch to PostgreSQL later.

### Step 1: Update Settings

Create a file `local_settings.py` in the `MarketLink` directory:

```python
# MarketLink/local_settings.py
# This file overrides settings for local development

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
```

### Step 2: Update manage.py

Temporarily modify `manage.py` to use local settings:

```python
# manage.py
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MarketLink.settings')

    # Use local settings if it exists (for development)
    if os.path.exists('MarketLink/local_settings.py'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MarketLink.local_settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(...) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

### Step 3: Run Migrations with SQLite

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Step 4: Switch Back to PostgreSQL

Once you have PostgreSQL properly set up:

1. Remove the `local_settings.py` file
2. Update `manage.py` back to use `MarketLink.settings` only
3. Create a new database with PostgreSQL user
4. Run migrations again

## Notes

- SQLite is **NOT** recommended for production
- Use SQLite only for development while setting up PostgreSQL
- Once PostgreSQL is working, delete `db.sqlite3` and switch back
- SQLite doesn't support some advanced PostgreSQL features (like certain locks)

## Quick Start with SQLite

```bash
# Create local_settings.py
echo "DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'db.sqlite3'}}" > MarketLink/local_settings.py

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver
```
