-- upgrade --
CREATE TABLE IF NOT EXISTS "tenants_captcha" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL,
    "value" VARCHAR(32) NOT NULL
);
CREATE TABLE IF NOT EXISTS "tenants_changelogs" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id_tenant" UUID NOT NULL,
    "model" VARCHAR(64) NOT NULL
);
CREATE TABLE IF NOT EXISTS "tenants_lookup_org_units" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "code" VARCHAR(128) NOT NULL,
    "order" INT,
    CONSTRAINT "uid_tenants_loo_id_tena_ee331b" UNIQUE ("id_tenant", "code")
);
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_touched_a2bb14" ON "tenants_lookup_org_units" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_active_665bed" ON "tenants_lookup_org_units" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_merged__1f901b" ON "tenants_lookup_org_units" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_id_tena_821fb8" ON "tenants_lookup_org_units" ("id_tenant");
CREATE TABLE IF NOT EXISTS "tenants_lookups_prefered_language" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "code" VARCHAR(128) NOT NULL,
    "order" INT,
    CONSTRAINT "uid_tenants_loo_id_tena_a6e277" UNIQUE ("id_tenant", "code")
);
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_touched_ad2f86" ON "tenants_lookups_prefered_language" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_active_c28111" ON "tenants_lookups_prefered_language" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_merged__46c9be" ON "tenants_lookups_prefered_language" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_id_tena_a48427" ON "tenants_lookups_prefered_language" ("id_tenant");
CREATE TABLE IF NOT EXISTS "tenants_lookup_user_groups" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "code" VARCHAR(128) NOT NULL,
    "order" INT,
    "group_code" VARCHAR(32) NOT NULL,
    CONSTRAINT "uid_tenants_loo_id_tena_4abb24" UNIQUE ("id_tenant", "code", "group_code")
);
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_touched_67d943" ON "tenants_lookup_user_groups" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_active_3dfc47" ON "tenants_lookup_user_groups" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_merged__ee57a9" ON "tenants_lookup_user_groups" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_id_tena_f03dba" ON "tenants_lookup_user_groups" ("id_tenant");
CREATE TABLE IF NOT EXISTS "tenants_lookup_user_permissions" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "code" VARCHAR(128) NOT NULL,
    "order" INT,
    CONSTRAINT "uid_tenants_loo_id_tena_6a6ce9" UNIQUE ("id_tenant", "code")
);
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_touched_ff617a" ON "tenants_lookup_user_permissions" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_active_3a2d1a" ON "tenants_lookup_user_permissions" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_merged__1929b9" ON "tenants_lookup_user_permissions" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_id_tena_6cd4d7" ON "tenants_lookup_user_permissions" ("id_tenant");
CREATE TABLE IF NOT EXISTS "tenants_lookup_user_roles" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "code" VARCHAR(128) NOT NULL,
    "order" INT,
    CONSTRAINT "uid_tenants_loo_id_tena_4cc6dc" UNIQUE ("id_tenant", "code")
);
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_touched_6dcc9a" ON "tenants_lookup_user_roles" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_active_890d43" ON "tenants_lookup_user_roles" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_merged__08d205" ON "tenants_lookup_user_roles" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_tenants_loo_id_tena_2b7255" ON "tenants_lookup_user_roles" ("id_tenant");
CREATE TABLE IF NOT EXISTS "tenants_options" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "key" VARCHAR(128) NOT NULL,
    "value" TEXT,
    CONSTRAINT "uid_tenants_opt_id_tena_77b16f" UNIQUE ("id_tenant", "key")
);
CREATE INDEX IF NOT EXISTS "idx_tenants_opt_touched_e89790" ON "tenants_options" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_opt_active_f7b1be" ON "tenants_options" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_opt_merged__21c912" ON "tenants_options" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_tenants_opt_id_tena_5111fd" ON "tenants_options" ("id_tenant");
CREATE TABLE IF NOT EXISTS "tenants_register_users_queue" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "first_name" VARCHAR(128),
    "last_name" VARCHAR(128),
    "username" VARCHAR(64),
    "password" VARCHAR(128),
    "email" VARCHAR(128),
    "mobile_phone" VARCHAR(128),
    "pin" VARCHAR(8) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_tenants_reg_touched_cb97a7" ON "tenants_register_users_queue" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_reg_active_bc0274" ON "tenants_register_users_queue" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_reg_merged__1ada84" ON "tenants_register_users_queue" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_tenants_reg_id_tena_74d807" ON "tenants_register_users_queue" ("id_tenant");
CREATE TABLE IF NOT EXISTS "tenants" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "code" VARCHAR(64) NOT NULL UNIQUE,
    "name" TEXT NOT NULL,
    "search_term" TEXT
);
CREATE INDEX IF NOT EXISTS "idx_tenants_touched_694a80" ON "tenants" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_active_54a007" ON "tenants" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_merged__9032f0" ON "tenants" ("merged_with");
CREATE TABLE IF NOT EXISTS "tenants_translation_lookup_org_units" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "lookup_id" UUID NOT NULL REFERENCES "tenants_lookup_org_units" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_tenants_tra_lookup__cc1796" ON "tenants_translation_lookup_org_units" ("lookup_id");
CREATE TABLE IF NOT EXISTS "tenants_translation_lookups_prefered_language" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "lookup_id" UUID NOT NULL REFERENCES "tenants_lookups_prefered_language" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_tenants_tra_lookup__0df124" ON "tenants_translation_lookups_prefered_language" ("lookup_id");
CREATE TABLE IF NOT EXISTS "tenants_translation_lookup_user_groups" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "lookup_id" UUID NOT NULL REFERENCES "tenants_lookup_user_groups" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_tenants_tra_lookup__33b677" ON "tenants_translation_lookup_user_groups" ("lookup_id");
CREATE TABLE IF NOT EXISTS "tenants_translation_lookup_user_permissions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "lookup_id" UUID NOT NULL REFERENCES "tenants_lookup_user_permissions" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_tenants_tra_lookup__b9a5f5" ON "tenants_translation_lookup_user_permissions" ("lookup_id");
CREATE TABLE IF NOT EXISTS "tenants_translation_lookup_user_roles" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "lookup_id" UUID NOT NULL REFERENCES "tenants_lookup_user_roles" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_tenants_tra_lookup__d3f647" ON "tenants_translation_lookup_user_roles" ("lookup_id");
CREATE TABLE IF NOT EXISTS "tenants_users" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "uid" VARCHAR(7) NOT NULL,
    "username" VARCHAR(255),
    "password" VARCHAR(128),
    "first_name" VARCHAR(128),
    "last_name" VARCHAR(128),
    "profile_picture" VARCHAR(128),
    "email" VARCHAR(128),
    "mobile_phone" VARCHAR(128),
    "mobile_phone_is_verified" BOOL NOT NULL  DEFAULT False,
    "email_is_verified" BOOL NOT NULL  DEFAULT False,
    "account_verified" BOOL NOT NULL  DEFAULT False,
    "reset_password_uuid" UUID  UNIQUE,
    "reset_password_uuid_expiration_timestamp" TIMESTAMPTZ,
    "pin_login_uuid" UUID  UNIQUE,
    "pin_login_pin" VARCHAR(32),
    "delete_account_key" UUID  UNIQUE,
    "delete_account_pin" VARCHAR(32),
    "delete_account_key_expired_after" TIMESTAMPTZ,
    "delete_account_timestamp" TIMESTAMPTZ,
    "no_search" BOOL,
    "data" JSONB,
    "role_id" UUID REFERENCES "tenants_lookup_user_roles" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_tenants_use_id_tena_0ba431" UNIQUE ("id_tenant", "uid"),
    CONSTRAINT "uid_tenants_use_id_tena_45ae81" UNIQUE ("id_tenant", "username"),
    CONSTRAINT "uid_tenants_use_id_tena_9af9b8" UNIQUE ("id_tenant", "email", "active"),
    CONSTRAINT "uid_tenants_use_id_tena_6c93cb" UNIQUE ("id_tenant", "mobile_phone", "active")
);
CREATE INDEX IF NOT EXISTS "idx_tenants_use_touched_944d4d" ON "tenants_users" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_use_active_3f4e40" ON "tenants_users" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_use_merged__0dd12c" ON "tenants_users" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_tenants_use_id_tena_47137d" ON "tenants_users" ("id_tenant");
CREATE TABLE IF NOT EXISTS "tenants_c11_users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "display_name" VARCHAR(255),
    "display_name_lc" VARCHAR(255),
    "last_name_lc" VARCHAR(255),
    "created_by_display_name" VARCHAR(255),
    "last_updated_by_display_name" VARCHAR(255),
    "created_by_display_profile_picture" VARCHAR(255),
    "last_updated_by_display_profile_picture" VARCHAR(255),
    "search" TEXT,
    "user_id" UUID NOT NULL UNIQUE REFERENCES "tenants_users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "tenants_sessions" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "ttl" INT   DEFAULT 604800,
    "expires_on" TIMESTAMPTZ,
    "user_id" UUID NOT NULL REFERENCES "tenants_users" ("id") ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS "idx_tenants_ses_touched_2965ba" ON "tenants_sessions" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_ses_active_8c8dea" ON "tenants_sessions" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_ses_merged__4490d8" ON "tenants_sessions" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_tenants_ses_id_tena_29e9c6" ON "tenants_sessions" ("id_tenant");
CREATE TABLE IF NOT EXISTS "tenants_user_settings" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "key" VARCHAR(128) NOT NULL,
    "value" TEXT NOT NULL,
    "user_id" UUID NOT NULL REFERENCES "tenants_users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_tenants_use_user_id_5aeb11" UNIQUE ("user_id", "key")
);
CREATE INDEX IF NOT EXISTS "idx_tenants_use_touched_c084e5" ON "tenants_user_settings" ("touched");
CREATE INDEX IF NOT EXISTS "idx_tenants_use_active_c69e39" ON "tenants_user_settings" ("active");
CREATE INDEX IF NOT EXISTS "idx_tenants_use_merged__1777bf" ON "tenants_user_settings" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_tenants_use_id_tena_fc1cd6" ON "tenants_user_settings" ("id_tenant");
CREATE INDEX IF NOT EXISTS "idx_tenants_use_user_id_7b38d0" ON "tenants_user_settings" ("user_id");
CREATE TABLE IF NOT EXISTS "tenants_lookup_user_groups_tenants_users" (
    "tenants_lookup_user_groups_id" UUID NOT NULL REFERENCES "tenants_lookup_user_groups" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "tenants_users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "tenants_lookup_user_roles_tenants_lookup_user_permissions" (
    "tenants_lookup_user_roles_id" UUID NOT NULL REFERENCES "tenants_lookup_user_roles" ("id") ON DELETE CASCADE,
    "lookupuserpermission_id" UUID NOT NULL REFERENCES "tenants_lookup_user_permissions" ("id") ON DELETE CASCADE
);
