#!/usr/bin/env python
"""
PostgreSQL Setup Script for MarketLink
Run this script to automatically create the database and user
"""

import subprocess
import sys
import os

def run_command(cmd, shell=False):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def setup_postgresql():
    """Setup PostgreSQL database and user"""
    print("=" * 60)
    print("MarketLink PostgreSQL Setup")
    print("=" * 60)
    
    # SQL commands to execute
    sql_commands = [
        "CREATE DATABASE marketlink WITH ENCODING = 'UTF8' TEMPLATE = template0;",
        "CREATE USER marketlink_user WITH PASSWORD 'marketlink_password';",
        "ALTER ROLE marketlink_user SET client_encoding TO 'utf8';",
        "ALTER ROLE marketlink_user SET default_transaction_isolation TO 'read committed';",
        "GRANT ALL PRIVILEGES ON DATABASE marketlink TO marketlink_user;",
        "\\c marketlink",
        "GRANT ALL ON SCHEMA public TO marketlink_user;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO marketlink_user;",
    ]
    
    # Try to find psql
    psql_paths = [
        "psql",  # In PATH
        "C:\\Program Files\\PostgreSQL\\15\\bin\\psql.exe",
        "C:\\Program Files\\PostgreSQL\\14\\bin\\psql.exe",
        "C:\\Program Files\\PostgreSQL\\16\\bin\\psql.exe",
        "C:\\Program Files (x86)\\PostgreSQL\\15\\bin\\psql.exe",
    ]
    
    psql_cmd = None
    for path in psql_paths:
        ret, out, err = run_command(f'"{path}" --version', shell=True)
        if ret == 0:
            psql_cmd = path
            print(f"✓ Found PostgreSQL at: {path}")
            print(f"  Version: {out.strip()}")
            break
    
    if not psql_cmd:
        print("\n✗ PostgreSQL not found!")
        print("\nTried these locations:")
        for path in psql_paths:
            print(f"  - {path}")
        print("\nPlease ensure PostgreSQL is installed and in your PATH.")
        return False
    
    # Create SQL script file
    sql_file = "setup.sql"
    with open(sql_file, 'w') as f:
        for cmd in sql_commands:
            f.write(cmd + "\n")
    
    print(f"\n✓ Created SQL script: {sql_file}")
    
    # Execute SQL script
    print("\nExecuting SQL commands...")
    print("-" * 60)
    
    ret, out, err = run_command(f'"{psql_cmd}" -U postgres -f {sql_file}', shell=True)
    
    if ret == 0:
        print("✓ PostgreSQL setup completed successfully!")
        print("\nOutput:")
        print(out)
        
        # Clean up
        os.remove(sql_file)
        
        return True
    else:
        print("✗ Error during setup:")
        print(err if err else out)
        
        # Show detailed error help
        if "FATAL" in err or "password authentication" in err:
            print("\n" + "=" * 60)
            print("PASSWORD AUTHENTICATION ERROR")
            print("=" * 60)
            print("\nThe password you entered for the 'postgres' superuser was incorrect.")
            print("\nTo fix this:")
            print("1. Open PostgreSQL Command Line (SQL Shell)")
            print("2. When prompted, enter the correct superuser password")
            print("3. Then run this script again")
            print("\nOr, manually run the SQL commands from marketlink_setup.sql")
        
        return False

if __name__ == "__main__":
    success = setup_postgresql()
    sys.exit(0 if success else 1)
