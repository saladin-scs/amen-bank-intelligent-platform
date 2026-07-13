-- Amen Bank Platform — PostgreSQL initialization
-- Creates separate schemas for auth and banking services.

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS banking;

GRANT ALL ON SCHEMA auth TO amenbank;
GRANT ALL ON SCHEMA banking TO amenbank;
