# PostgreSQL Authentication Fix - Quick Guide

## Issue

```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed:
FATAL: password authentication failed for user "marketlink_user"
```

This error means PostgreSQL user `marketlink_user` doesn't exist or has the wrong password.

## Solution Options

### Option 1: Using pgAdmin (GUI - Easiest for Windows)

1. **Open pgAdmin**

   - Search for "pgAdmin" in Windows Start Menu
   - Or open http://localhost:5050 in your browser

2. **Login to pgAdmin**

   - Default email: pgadmin4@pgadmin.org
   - Default password: admin

3. **Create Database**

   - Right-click "Databases" → Create → Database
   - Name: `marketlink`
   - Click Save

4. **Create User/Role**

   - Right-click "Login/Group Roles" → Create → Login/Group Role
   - Name: `marketlink_user`
   - Tab: Definition
   - Password: `marketlink_password`
   - Click Save

5. **Grant Privileges**
   - Right-click database "marketlink" → Properties
   - Tab: Security
   - Select `marketlink_user` from Roles
   - Grant privileges: SELECT, INSERT, UPDATE, DELETE, CREATE, ALL

### Option 2: Using SQL Script

1. **Find PostgreSQL Installation Path**

   - Windows: Usually `C:\Program Files\PostgreSQL\15\bin`
   - Add to System PATH or use full path

2. **Run Setup Script**

   ```bash
   # Navigate to project directory
   cd E:\Practice(Python)\Softvence(Assignment)\MarketLink

   # Run the SQL script
   psql -U postgres -f marketlink_setup.sql

   # If psql not found, use full path:
   "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -f marketlink_setup.sql
   ```

3. **Enter PostgreSQL Admin Password**
   - When prompted, enter the password you set during PostgreSQL installation

### Option 3: Using Command Line (if psql is in PATH)

```bash
# Connect as postgres superuser
psql -U postgres

# In PostgreSQL shell, paste these commands:

-- Create database
CREATE DATABASE marketlink WITH ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TEMPLATE = template0;

-- Create user
CREATE USER marketlink_user WITH PASSWORD 'marketlink_password';

-- Configure user
ALTER ROLE marketlink_user SET client_encoding TO 'utf8';
ALTER ROLE marketlink_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE marketlink_user SET default_transaction_deferrable TO ON;

-- Grant all privileges on database
GRANT ALL PRIVILEGES ON DATABASE marketlink TO marketlink_user;

-- Grant schema privileges
\c marketlink
GRANT ALL ON SCHEMA public TO marketlink_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO marketlink_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO marketlink_user;

-- Exit
\q
```

### Option 4: Reset Existing User Password

If the user exists but password is wrong:

```bash
# Using psql as postgres user
psql -U postgres

-- Reset password:
ALTER USER marketlink_user WITH PASSWORD 'marketlink_password';

-- Exit
\q
```

## Step-by-Step for Windows Users

### Without pgAdmin:

1. **Open Command Prompt as Administrator**

   - Press `Win + R`
   - Type `cmd`
   - Press `Ctrl + Shift + Enter` for Admin

2. **Navigate to PostgreSQL bin directory**

   ```cmd
   cd C:\Program Files\PostgreSQL\15\bin
   ```

3. **Connect to PostgreSQL**

   ```cmd
   psql -U postgres
   ```

   - Enter your PostgreSQL superuser password when prompted

4. **Create Database and User**
   ```sql
   CREATE DATABASE marketlink WITH ENCODING = 'UTF8' TEMPLATE = template0;
   CREATE USER marketlink_user WITH PASSWORD 'marketlink_password';
   ALTER ROLE marketlink_user SET client_encoding TO 'utf8';
   GRANT ALL PRIVILEGES ON DATABASE marketlink TO marketlink_user;
   \c marketlink
   GRANT ALL ON SCHEMA public TO marketlink_user;
   \q
   ```

## Verify Connection Works

### Method 1: From Command Line

```bash
# Test connection directly
psql -U marketlink_user -d marketlink -h localhost -W

# When prompted, enter password: marketlink_password
# You should see: marketlink=>
```

### Method 2: From Django

```bash
# Run Django shell
python manage.py shell

# In Python:
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✓ Database connection successful!")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

### Method 3: Quick Check

```bash
# Run migrations (this will test the connection)
python manage.py migrate
```

## If Still Having Issues

### Check PostgreSQL Service is Running

**Windows:**

1. Open Services (Press `Win + R`, type `services.msc`)
2. Look for "postgresql-x64-15" or similar
3. If stopped, right-click and select "Start"

**Command line check:**

```bash
# Check if PostgreSQL is listening on port 5432
netstat -ano | findstr :5432
```

### Verify .env Configuration

Your `.env` file should have:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=marketlink
DB_USER=marketlink_user
DB_PASSWORD=marketlink_password
DB_HOST=localhost
DB_PORT=5432
```

### Update Settings if Different

If you used different credentials, update `.env` accordingly:

```env
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=your_port
```

## After Successful Connection

Run these Django commands:

```bash
# Create migrations (if not already created)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser for admin
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Temporary Fallback: Use SQLite

If you're still having issues with PostgreSQL, you can temporarily use SQLite:

1. **Revert to SQLite in settings.py:**

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

2. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

3. **Fix PostgreSQL later and switch back**

## Additional Help

- Check PostgreSQL logs: `C:\Program Files\PostgreSQL\15\data\log\postgresql.log`
- PostgreSQL documentation: https://www.postgresql.org/docs/current/
- psycopg2 documentation: https://www.psycopg.org/
