-- PostgreSQL Setup Script for MarketLink
-- Run this script using: psql -U postgres -f marketlink_setup.sql

-- Drop existing database and user if they exist (optional, for fresh setup)
-- DROP DATABASE IF EXISTS marketlink;
-- DROP USER IF EXISTS marketlink_user;

-- Create database
CREATE DATABASE marketlink
    WITH
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Create user
CREATE USER marketlink_user WITH PASSWORD 'marketlink_password';

-- Configure user connection settings
ALTER ROLE marketlink_user SET client_encoding TO 'utf8';
ALTER ROLE marketlink_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE marketlink_user SET default_transaction_deferrable TO ON;
ALTER ROLE marketlink_user SET default_transaction_level TO 'read committed';
ALTER ROLE marketlink_user SET statement_timeout TO 0;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE marketlink TO marketlink_user;

-- Connect to the new database
\c marketlink

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO marketlink_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO marketlink_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO marketlink_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO marketlink_user;

-- Verify setup
\du
\l
