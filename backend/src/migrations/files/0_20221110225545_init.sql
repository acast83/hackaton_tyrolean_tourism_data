-- upgrade --
CREATE TABLE IF NOT EXISTS "files_options" (
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
    CONSTRAINT "uid_files_optio_id_tena_c7431b" UNIQUE ("id_tenant", "key")
);
CREATE INDEX IF NOT EXISTS "idx_files_optio_touched_15dd5d" ON "files_options" ("touched");
CREATE INDEX IF NOT EXISTS "idx_files_optio_active_ea8513" ON "files_options" ("active");
CREATE INDEX IF NOT EXISTS "idx_files_optio_merged__34023f" ON "files_options" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_files_optio_id_tena_e750f1" ON "files_options" ("id_tenant");
