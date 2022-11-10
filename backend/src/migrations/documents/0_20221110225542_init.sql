-- upgrade --
CREATE TABLE IF NOT EXISTS "documents" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "instance" VARCHAR(128),
    "id_instance" VARCHAR(128) NOT NULL,
    "order_on_instance" INT,
    "path_on_instance" VARCHAR(255) NOT NULL  DEFAULT '/',
    "order_on_instance_path" INT,
    "filename" VARCHAR(255),
    "filesize" INT,
    "filetype" VARCHAR(32),
    "document_type_code" VARCHAR(128),
    "document_description" TEXT,
    "hash256" VARCHAR(255),
    "owner_rwd_policy" JSONB NOT NULL,
    "default_user_groups_rwd_policy" JSONB NOT NULL,
    "default_users_rwd_policy" JSONB NOT NULL,
    "default_all_unauthorized_rwd_policy" JSONB NOT NULL,
    "location" VARCHAR(255),
    "thumbnail" VARCHAR(255),
    "metadata" JSONB
);
CREATE INDEX IF NOT EXISTS "idx_documents_touched_32bdc7" ON "documents" ("touched");
CREATE INDEX IF NOT EXISTS "idx_documents_active_8e2030" ON "documents" ("active");
CREATE INDEX IF NOT EXISTS "idx_documents_merged__5d40cf" ON "documents" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_documents_id_tena_fe4c2e" ON "documents" ("id_tenant");
CREATE INDEX IF NOT EXISTS "idx_documents_id_inst_db49c8" ON "documents" ("id_instance");
CREATE INDEX IF NOT EXISTS "idx_documents_instanc_10de89" ON "documents" ("instance", "id_instance");
CREATE TABLE IF NOT EXISTS "documents_cache_11" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_by_display_name" VARCHAR(255),
    "last_updated_by_display_name" VARCHAR(255),
    "created_by_display_profile_picture" VARCHAR(255),
    "last_updated_by_display_profile_picture" VARCHAR(255),
    "shared_with_list_of_users_with_profile_pictures" JSONB,
    "shared_with_list_of_user_groups" JSONB,
    "document_id" UUID NOT NULL UNIQUE REFERENCES "documents" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "documents_shared_user_groups" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "can_read" BOOL NOT NULL  DEFAULT True,
    "can_modify" BOOL NOT NULL  DEFAULT False,
    "can_delete" BOOL NOT NULL  DEFAULT False,
    "id_user_group" UUID NOT NULL,
    "document_id" UUID NOT NULL REFERENCES "documents" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_documents_s_documen_d37a24" UNIQUE ("document_id", "id_user_group")
);
CREATE TABLE IF NOT EXISTS "documents_shared_users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "can_read" BOOL NOT NULL  DEFAULT True,
    "can_modify" BOOL NOT NULL  DEFAULT False,
    "can_delete" BOOL NOT NULL  DEFAULT False,
    "id_user" UUID NOT NULL,
    "document_id" UUID NOT NULL REFERENCES "documents" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_documents_s_documen_b80f74" UNIQUE ("document_id", "id_user")
);
CREATE TABLE IF NOT EXISTS "documents_options" (
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
    CONSTRAINT "uid_documents_o_id_tena_18354f" UNIQUE ("id_tenant", "key")
);
CREATE INDEX IF NOT EXISTS "idx_documents_o_touched_38f814" ON "documents_options" ("touched");
CREATE INDEX IF NOT EXISTS "idx_documents_o_active_bcfc03" ON "documents_options" ("active");
CREATE INDEX IF NOT EXISTS "idx_documents_o_merged__8ffd53" ON "documents_options" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_documents_o_id_tena_dc4de5" ON "documents_options" ("id_tenant");
