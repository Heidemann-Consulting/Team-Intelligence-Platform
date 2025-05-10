-- File: init_db.sql
-- Purpose: Initializes the PostgreSQL database schema for the ULACM Service v2.0.
-- This script creates tables, constraints, indexes, and sets up full-text search.
-- Added initial "Admin System Team" record.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'content_item_type_enum') THEN
        CREATE TYPE content_item_type_enum AS ENUM ('DOCUMENT', 'TEMPLATE', 'WORKFLOW');
    ELSE
        RAISE NOTICE 'Enum content_item_type_enum already exists. Manual review might be needed if values differ.';
    END IF;
END$$;

-- =============================================
-- TEAMS Table
-- Stores information about team accounts.
-- Corresponds to SRS 7.3.1.
-- =============================================
CREATE TABLE IF NOT EXISTS teams (
    team_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_name VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_teams_username_lower ON teams (lower(username));
CREATE INDEX IF NOT EXISTS idx_teams_team_name_lower ON teams (lower(team_name));

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_teams_updated_at ON teams;
CREATE TRIGGER update_teams_updated_at
BEFORE UPDATE ON teams
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- CONTENT_VERSIONS Table
-- Stores the actual content for each version of each item.
-- Corresponds to SRS 7.3.3.
-- saved_by_team_id remains NOT NULL. For admin actions on Templates/Workflows,
-- it will point to the ADMIN_SYSTEM_TEAM_ID.
-- =============================================
CREATE TABLE IF NOT EXISTS content_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID NOT NULL, -- Foreign key added later after content_items table exists
    markdown_content TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    saved_by_team_id UUID NOT NULL REFERENCES teams(team_id) ON DELETE SET NULL, -- Team that saved this version, or Admin System Team
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    content_tsv tsvector,
    CONSTRAINT uq_item_version_number UNIQUE (item_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_content_versions_item_id ON content_versions (item_id);
CREATE INDEX IF NOT EXISTS idx_content_versions_saved_by_team_id ON content_versions (saved_by_team_id);
CREATE INDEX IF NOT EXISTS idx_content_versions_item_id_created_at ON content_versions (item_id, created_at);
CREATE INDEX IF NOT EXISTS idx_gin_content_versions_content_tsv ON content_versions USING gin(content_tsv);

DROP TRIGGER IF EXISTS tsvectorupdate ON content_versions;
CREATE TRIGGER tsvectorupdate
BEFORE INSERT OR UPDATE ON content_versions
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(content_tsv, 'pg_catalog.english', markdown_content);

-- =============================================
-- CONTENT_ITEMS Table
-- Stores metadata for Documents, Templates, and Workflows.
-- team_id is NOT NULL. For Admin-created Templates/Workflows, it points to ADMIN_SYSTEM_TEAM_ID.
-- Corresponds to SRS 7.3.2.
-- =============================================
CREATE TABLE IF NOT EXISTS content_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE, -- Owning team OR Admin System Team
    item_type content_item_type_enum NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_globally_visible BOOLEAN NOT NULL DEFAULT FALSE, -- For Admin T/W, this will be TRUE
    current_version_id UUID NULL REFERENCES content_versions(version_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_team_item_name_type UNIQUE (team_id, name, item_type) -- Uniqueness per owner (team or admin system team)
);

CREATE INDEX IF NOT EXISTS idx_content_items_team_id ON content_items (team_id);
CREATE INDEX IF NOT EXISTS idx_content_items_item_type ON content_items (item_type);
CREATE INDEX IF NOT EXISTS idx_content_items_name_lower_team ON content_items (team_id, lower(name), item_type); -- More specific for uniqueness check
CREATE INDEX IF NOT EXISTS idx_content_items_created_at ON content_items (created_at);
CREATE INDEX IF NOT EXISTS idx_content_items_current_version_id ON content_items (current_version_id);
CREATE INDEX IF NOT EXISTS idx_gin_content_items_name_tsv ON content_items USING gin(to_tsvector('english', name));

DROP TRIGGER IF EXISTS update_content_items_updated_at ON content_items;
CREATE TRIGGER update_content_items_updated_at
BEFORE UPDATE ON content_items
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- Add Foreign Key Constraint (Circular Dependency Handling)
-- =============================================
DO $$
BEGIN
   IF NOT EXISTS (
       SELECT 1 FROM information_schema.table_constraints
       WHERE constraint_name = 'fk_content_versions_item_id' AND table_name = 'content_versions'
   ) THEN
      ALTER TABLE content_versions
      ADD CONSTRAINT fk_content_versions_item_id
      FOREIGN KEY (item_id) REFERENCES content_items(item_id) ON DELETE CASCADE;
   END IF;
END $$;

-- =============================================
-- Initial Data
-- =============================================
-- Insert the Admin System Team (use the fixed UUID from config.py)
-- Hashed password for 'admin_system_password' (example, should be strong & ideally not used for login)
-- For bcrypt, a generated hash would be like: '$2b$12$abcdefghijklmnopqrstuv.abcdefghijklmnopqrstuv.abcdefghijkl'
-- This is a placeholder hash for 'admin_system_password_placeholder'.
-- In a real scenario, if this team needed to "log in" (it doesn't), this password would be generated securely.
-- Since it's a system entity, it doesn't log in. Hashed password field still needs a value.
INSERT INTO teams (team_id, team_name, username, hashed_password, is_active)
VALUES (
    '04a9a4ec-18d8-4cfd-bead-d0ef99199e17', -- Must match frontend ADMIN_SYSTEM_TEAM_ID_STRING in ulacm_frontend/src/utils/constants.ts
    'ULACM System Administrators',
    '_ulacm_admin_system_team_', -- Unique system username, not for direct login
    '$2b$12$DUMMYHASHFORADMINSYSTEMTEAMACCOUNTDONTUSEME', -- Placeholder non-functional hash
    TRUE
) ON CONFLICT (team_id) DO NOTHING;


-- =============================================
-- Script Completion Message
-- =============================================
DO $$ BEGIN
    RAISE NOTICE 'ULACM Database Initialization Script Completed (with Admin System Team).';
END $$;
