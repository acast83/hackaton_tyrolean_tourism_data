-- upgrade --
CREATE TABLE IF NOT EXISTS "flows_lookups_flow_priorities" (
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
    CONSTRAINT "uid_flows_looku_id_tena_1b998f" UNIQUE ("id_tenant", "code")
);
CREATE INDEX IF NOT EXISTS "idx_flows_looku_touched_1c729f" ON "flows_lookups_flow_priorities" ("touched");
CREATE INDEX IF NOT EXISTS "idx_flows_looku_active_fe435a" ON "flows_lookups_flow_priorities" ("active");
CREATE INDEX IF NOT EXISTS "idx_flows_looku_merged__c9d31e" ON "flows_lookups_flow_priorities" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_flows_looku_id_tena_3dbf9b" ON "flows_lookups_flow_priorities" ("id_tenant");
CREATE TABLE IF NOT EXISTS "flows_lookup_flow_types" (
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
    CONSTRAINT "uid_flows_looku_id_tena_088b92" UNIQUE ("id_tenant", "code")
);
CREATE INDEX IF NOT EXISTS "idx_flows_looku_touched_69f55b" ON "flows_lookup_flow_types" ("touched");
CREATE INDEX IF NOT EXISTS "idx_flows_looku_active_e71f61" ON "flows_lookup_flow_types" ("active");
CREATE INDEX IF NOT EXISTS "idx_flows_looku_merged__39420a" ON "flows_lookup_flow_types" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_flows_looku_id_tena_1e3a4a" ON "flows_lookup_flow_types" ("id_tenant");
CREATE TABLE IF NOT EXISTS "flows_lookups_flow_visibility" (
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
    CONSTRAINT "uid_flows_looku_id_tena_2f91be" UNIQUE ("id_tenant", "code")
);
CREATE INDEX IF NOT EXISTS "idx_flows_looku_touched_d9c832" ON "flows_lookups_flow_visibility" ("touched");
CREATE INDEX IF NOT EXISTS "idx_flows_looku_active_d04c6e" ON "flows_lookups_flow_visibility" ("active");
CREATE INDEX IF NOT EXISTS "idx_flows_looku_merged__7b9437" ON "flows_lookups_flow_visibility" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_flows_looku_id_tena_16b791" ON "flows_lookups_flow_visibility" ("id_tenant");
CREATE TABLE IF NOT EXISTS "flows" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "instance" VARCHAR(32) NOT NULL,
    "id_instance" UUID NOT NULL,
    "important" BOOL   DEFAULT False,
    "archived" BOOL NOT NULL  DEFAULT False,
    "html" TEXT,
    "text" TEXT,
    "data" JSONB,
    "attached_documents" JSONB,
    "mentioned_persons" JSONB,
    "email_sent_to" JSONB,
    "timesheet_logged" JSONB,
    "last_created_timestamp_for_auto_merged_flows" TIMESTAMPTZ,
    "parent_1st_level" UUID,
    "parent_2nd_level" UUID,
    "parent_3rd_level" UUID,
    "automatically_merged_with_id" UUID REFERENCES "flows" ("id") ON DELETE CASCADE,
    "priority_id" UUID REFERENCES "flows_lookups_flow_priorities" ("id") ON DELETE CASCADE,
    "type_id" UUID NOT NULL REFERENCES "flows_lookup_flow_types" ("id") ON DELETE CASCADE,
    "visibility_id" UUID REFERENCES "flows_lookups_flow_visibility" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_flows_touched_22b58f" ON "flows" ("touched");
CREATE INDEX IF NOT EXISTS "idx_flows_active_f52e1a" ON "flows" ("active");
CREATE INDEX IF NOT EXISTS "idx_flows_merged__26dfb1" ON "flows" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_flows_id_tena_4a7dfe" ON "flows" ("id_tenant");
CREATE INDEX IF NOT EXISTS "idx_flows_instanc_1facb0" ON "flows" ("instance");
CREATE INDEX IF NOT EXISTS "idx_flows_id_inst_5d33e1" ON "flows" ("id_instance");
CREATE INDEX IF NOT EXISTS "idx_flows_parent__5f011f" ON "flows" ("parent_1st_level");
CREATE INDEX IF NOT EXISTS "idx_flows_parent__006de6" ON "flows" ("parent_2nd_level");
CREATE INDEX IF NOT EXISTS "idx_flows_parent__12c5ad" ON "flows" ("parent_3rd_level");
CREATE INDEX IF NOT EXISTS "idx_flows_priorit_7e0440" ON "flows" ("priority_id");
CREATE INDEX IF NOT EXISTS "idx_flows_type_id_587e3f" ON "flows" ("type_id");
CREATE INDEX IF NOT EXISTS "idx_flows_visibil_fe851f" ON "flows" ("visibility_id");
CREATE TABLE IF NOT EXISTS "flows_cache_11_flows" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "attached_documents_info" JSONB,
    "mentioned_persons_info" JSONB,
    "created_by_display_name" VARCHAR(255),
    "created_by_profile_picture" VARCHAR(255),
    "flow_id" UUID NOT NULL UNIQUE REFERENCES "flows" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "flows_cache_1n" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "search" TEXT,
    "flow_id" UUID NOT NULL REFERENCES "flows" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "flows_options" (
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
    CONSTRAINT "uid_flows_optio_id_tena_96d4fa" UNIQUE ("id_tenant", "key")
);
CREATE INDEX IF NOT EXISTS "idx_flows_optio_touched_5580a1" ON "flows_options" ("touched");
CREATE INDEX IF NOT EXISTS "idx_flows_optio_active_d26431" ON "flows_options" ("active");
CREATE INDEX IF NOT EXISTS "idx_flows_optio_merged__3e8b57" ON "flows_options" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_flows_optio_id_tena_2ef21f" ON "flows_options" ("id_tenant");
CREATE TABLE IF NOT EXISTS "flows_translation_lookup_flow_types" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "lookup_id" UUID NOT NULL REFERENCES "flows_lookup_flow_types" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_flows_trans_lookup__01149c" ON "flows_translation_lookup_flow_types" ("lookup_id");
CREATE TABLE IF NOT EXISTS "flows_translation_lookups_flow_priorities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "lookup_id" UUID NOT NULL REFERENCES "flows_lookups_flow_priorities" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_flows_trans_lookup__38438f" ON "flows_translation_lookups_flow_priorities" ("lookup_id");
CREATE TABLE IF NOT EXISTS "flows_translation_lookups_flow_visibility" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "lookup_id" UUID NOT NULL REFERENCES "flows_lookups_flow_visibility" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_flows_trans_lookup__67549e" ON "flows_translation_lookups_flow_visibility" ("lookup_id");
