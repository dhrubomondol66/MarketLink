# PostgreSQL Setup Guide for MarketLink

## Windows Setup

### Option 1: Using PostgreSQL Installer

1. **Download PostgreSQL**

   - Visit https://www.postgresql.org/download/windows/
   - Download PostgreSQL 15 or latest version

2. **Install PostgreSQL**

   - Run the installer
   - Choose installation directory (default is usually fine)
   - Set superuser (postgres) password - **REMEMBER THIS**
   - Port: 5432 (default)
   - Locale: [Default locale]
   - Complete the installation

3. **Verify Installation**

   ```bash
   psql --version
   ```

4. **Create Database and User**

   ```bash
   # Connect as postgres user
   psql -U postgres

   # In PostgreSQL shell, execute:
   CREATE DATABASE marketlink;
   CREATE USER marketlink_user WITH PASSWORD 'marketlink_password';
   ALTER ROLE marketlink_user SET client_encoding TO 'utf8';
   ALTER ROLE marketlink_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE marketlink_user SET default_transaction_deferrable TO ON;
   ALTER ROLE marketlink_user SET default_transaction_level TO 'read committed';
   GRANT ALL PRIVILEGES ON DATABASE marketlink TO marketlink_user;
   \q
   ```

### Option 2: Using Chocolatey (Windows)

```bash
# Install PostgreSQL via Chocolatey
choco install postgresql15

# Set environment variables and create database as in Option 1
```

### Option 3: Using Docker (Recommended)

```bash
# Pull PostgreSQL image
docker pull postgres:15

# Run PostgreSQL container
docker run --name marketlink-db \
  -e POSTGRES_DB=marketlink \
  -e POSTGRES_USER=marketlink_user \
  -e POSTGRES_PASSWORD=marketlink_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  -d postgres:15

# Verify container is running
docker ps
```

## macOS Setup

### Option 1: Using Homebrew

```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create database and user
createdb -U postgres marketlink
psql -U postgres -d marketlink

# In PostgreSQL shell:
CREATE USER marketlink_user WITH PASSWORD 'marketlink_password';
ALTER DATABASE marketlink OWNER TO marketlink_user;
GRANT ALL PRIVILEGES ON DATABASE marketlink TO marketlink_user;
\q
```

### Option 2: Using Docker

```bash
# Same as Windows Option 3
docker run --name marketlink-db \
  -e POSTGRES_DB=marketlink \
  -e POSTGRES_USER=marketlink_user \
  -e POSTGRES_PASSWORD=marketlink_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  -d postgres:15
```

## Linux Setup (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres createdb marketlink
sudo -u postgres psql

# In PostgreSQL shell:
CREATE USER marketlink_user WITH PASSWORD 'marketlink_password';
ALTER DATABASE marketlink OWNER TO marketlink_user;
GRANT ALL PRIVILEGES ON DATABASE marketlink TO marketlink_user;
\q
```

## Connection Verification

### Test Connection from Command Line

```bash
# Using psql
psql -U marketlink_user -h localhost -d marketlink -W
# Password: marketlink_password

# If successful, you should see:
# marketlink=>
```

### Test Connection from Django

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run Django shell
python manage.py shell

# In Python shell:
from django.db import connection
try:
    connection.ensure_connection()
    print("Database connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")
exit()
```

## Environment Configuration

Update your `.env` file with PostgreSQL credentials:

```env
# PostgreSQL Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=marketlink
DB_USER=marketlink_user
DB_PASSWORD=marketlink_password
DB_HOST=localhost
DB_PORT=5432
```

## Run Migrations

After setting up PostgreSQL:

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Verify migrations
python manage.py showmigrations
```

## Backup and Restore

### Backup Database

```bash
# Full backup
pg_dump -U marketlink_user marketlink > marketlink_backup.sql

# Compressed backup
pg_dump -U marketlink_user -F c marketlink > marketlink_backup.dump
```

### Restore Database

```bash
# From SQL file
psql -U marketlink_user marketlink < marketlink_backup.sql

# From compressed file
pg_restore -U marketlink_user -d marketlink marketlink_backup.dump
```

## Troubleshooting

### Connection Refused Error

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS
Services panel  # Windows

# If not running, start it:
sudo systemctl start postgresql  # Linux
brew services start postgresql@15  # macOS
```

### Authentication Failed

```bash
# Reset password
sudo -u postgres psql
ALTER USER marketlink_user WITH PASSWORD 'marketlink_password';
\q
```

### Port Already in Use

```bash
# Change PostgreSQL port in postgresql.conf
# Linux/macOS: /etc/postgresql/15/main/postgresql.conf
# Windows: C:\Program Files\PostgreSQL\15\data\postgresql.conf

# Find line: port = 5432
# Change to: port = 5433 (or any available port)
# Update .env file accordingly
```

### Database Does Not Exist

```bash
# Create missing database
sudo -u postgres createdb marketlink

# Or using psql
psql -U postgres
CREATE DATABASE marketlink;
\q
```

## Performance Tips

### For Development

```sql
-- Reduce logging (in postgresql.conf)
log_min_duration_statement = 1000  -- Log slow queries > 1 second

-- Enable query statistics
shared_preload_libraries = 'pg_stat_statements'
```

### For Production

```sql
-- Connection pooling settings
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

## Additional Resources

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [Django Database Documentation](https://docs.djangoproject.com/en/4.2/ref/databases/postgresql/)
- [psycopg2 Documentation](https://www.psycopg.org/psycopg2/docs/)
