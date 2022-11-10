-- upgrade --
CREATE TABLE IF NOT EXISTS "sms_options" (
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
    CONSTRAINT "uid_sms_options_id_tena_a92d8b" UNIQUE ("id_tenant", "key")
);
CREATE INDEX IF NOT EXISTS "idx_sms_options_touched_3584af" ON "sms_options" ("touched");
CREATE INDEX IF NOT EXISTS "idx_sms_options_active_b617bb" ON "sms_options" ("active");
CREATE INDEX IF NOT EXISTS "idx_sms_options_merged__1b074a" ON "sms_options" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_sms_options_id_tena_d8b6b8" ON "sms_options" ("id_tenant");
CREATE TABLE IF NOT EXISTS "sms_received" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "from_number" VARCHAR(32) NOT NULL,
    "to_number" VARCHAR(32) NOT NULL,
    "message" TEXT,
    "raw" JSONB,
    "polled" TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS "idx_sms_receive_touched_27a433" ON "sms_received" ("touched");
CREATE INDEX IF NOT EXISTS "idx_sms_receive_active_5035f4" ON "sms_received" ("active");
CREATE INDEX IF NOT EXISTS "idx_sms_receive_merged__cc866e" ON "sms_received" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_sms_receive_id_tena_c5126a" ON "sms_received" ("id_tenant");
CREATE TABLE IF NOT EXISTS "sms_queue" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "target_number" VARCHAR(64) NOT NULL,
    "message" TEXT NOT NULL,
    "scheduled_not_send_before_timestamp" TIMESTAMPTZ,
    "sent_to_gateway" TIMESTAMPTZ,
    "external_id" VARCHAR(64),
    "price" DECIMAL(10,4),
    "initial_response" JSONB,
    "status" JSONB,
    "delivery_confirmed_timestamp" TIMESTAMPTZ,
    "delivery_report_response" JSONB,
    CONSTRAINT "uid_sms_queue_id_tena_46fba4" UNIQUE ("id_tenant", "external_id")
);
CREATE INDEX IF NOT EXISTS "idx_sms_queue_touched_8fac7d" ON "sms_queue" ("touched");
CREATE INDEX IF NOT EXISTS "idx_sms_queue_active_4a655d" ON "sms_queue" ("active");
CREATE INDEX IF NOT EXISTS "idx_sms_queue_merged__44de7c" ON "sms_queue" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_sms_queue_id_tena_9a0818" ON "sms_queue" ("id_tenant");
CREATE INDEX IF NOT EXISTS "idx_sms_queue_externa_dc092e" ON "sms_queue" ("external_id");
