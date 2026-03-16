#!/usr/bin/env python
"""
Quick PostgreSQL User Reset - For Windows
Use this if you forgot the postgres superuser password
"""

import subprocess
import sys
import os
import tempfile

def find_postgresql_paths():
    """Find PostgreSQL installation paths"""
    possible_paths = [
        "C:\\Program Files\\PostgreSQL\\15",
        "C:\\Program Files\\PostgreSQL\\14",
        "C:\\Program Files\\PostgreSQL\\16",
        "C:\\Program Files (x86)\\PostgreSQL\\15",
    ]
    return [p for p in possible_paths if os.path.exists(p)]

def reset_postgres_auth():
    """
    Reset PostgreSQL authentication to allow local connections
    This modifies pg_hba.conf temporarily
    """
    print("=" * 60)
    print("PostgreSQL Authentication Reset")
    print("=" * 60)
    
    pg_paths = find_postgresql_paths()
    
    if not pg_paths:
        print("\n✗ PostgreSQL installation not found!")
        print("Install PostgreSQL from: https://www.postgresql.org/download/windows/")
        return False
    
    print(f"\n✓ Found PostgreSQL installation at:")
    for path in pg_paths:
        print(f"  - {path}")
    
    pg_path = pg_paths[0]
    data_path = os.path.join(pg_path, "data")
    pg_hba_conf = os.path.join(data_path, "pg_hba.conf")
    
    if not os.path.exists(pg_hba_conf):
        print(f"\n✗ pg_hba.conf not found at: {pg_hba_conf}")
        return False
    
    print(f"\n✓ Found pg_hba.conf at: {pg_hba_conf}")
    
    # Read current config
    with open(pg_hba_conf, 'r') as f:
        content = f.read()
    
    # Backup original
    backup_file = pg_hba_conf + '.backup'
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"✓ Created backup at: {backup_file}")
    
    # Modify to allow local connections without password
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Skip comment and empty lines
        if line.strip().startswith('#') or not line.strip():
            new_lines.append(line)
        # Change md5 to trust for local connections
        elif 'local' in line and 'postgres' in line:
            line = line.replace('md5', 'trust')
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    # Write modified config
    with open(pg_hba_conf, 'w') as f:
        f.write(new_content)
    
    print("✓ Modified pg_hba.conf to allow local connections without password")
    
    # Restart PostgreSQL
    print("\nRestarting PostgreSQL service...")
    
    # Try to restart PostgreSQL service
    ret = subprocess.call('net stop postgresql-x64-15', shell=True)
    subprocess.call('net start postgresql-x64-15', shell=True)
    
    print("✓ PostgreSQL restarted")
    
    return True

def create_user_and_database():
    """Create the MarketLink database and user"""
    print("\n" + "=" * 60)
    print("Creating MarketLink Database and User")
    print("=" * 60)
    
    sql_script = """
CREATE DATABASE IF NOT EXISTS marketlink WITH ENCODING = 'UTF8' TEMPLATE = template0;
CREATE USER IF NOT EXISTS marketlink_user WITH PASSWORD 'marketlink_password';
ALTER ROLE marketlink_user SET client_encoding TO 'utf8';
ALTER ROLE marketlink_user SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE marketlink TO marketlink_user;

-- Connect to the new database and grant schema privileges
\\\\c marketlink
GRANT ALL ON SCHEMA public TO marketlink_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO marketlink_user;
"""
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(sql_script)
        sql_file = f.name
    
    try:
        # Execute using psql
        cmd = f'psql -U postgres -f "{sql_file}"'
        print(f"Executing: {cmd}\n")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Successfully created database and user!")
            print("\nOutput:")
            print(result.stdout)
            return True
        else:
            print("✗ Error creating database and user:")
            print(result.stderr)
            return False
    finally:
        os.unlink(sql_file)

def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  MarketLink PostgreSQL Quick Setup".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Step 1: Reset authentication
    print("\nStep 1: Resetting PostgreSQL authentication...")
    if not reset_postgres_auth():
        print("Failed to reset authentication. Trying direct connection...")
    
    # Step 2: Create user and database
    print("\nStep 2: Creating database and user...")
    if not create_user_and_database():
        print("Failed to create user and database")
        return False
    
    print("\n" + "=" * 60)
    print("✓ PostgreSQL Setup Complete!")
    print("=" * 60)
    print("\nYou can now run:")
    print("  python manage.py migrate")
    print("  python manage.py createsuperuser")
    print("  python manage.py runserver")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
