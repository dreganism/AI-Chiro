-- Create database only if it doesn't exist
SELECT 'CREATE DATABASE sjwg_reporter'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sjwg_reporter')\gexec
