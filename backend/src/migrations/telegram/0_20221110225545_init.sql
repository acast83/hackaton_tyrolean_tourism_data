-- upgrade --
CREATE TABLE IF NOT EXISTS "telegram_linked_accounts" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "telegram_id" BIGINT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS "idx_telegram_li_touched_4d0d35" ON "telegram_linked_accounts" ("touched");
CREATE INDEX IF NOT EXISTS "idx_telegram_li_active_3f80d1" ON "telegram_linked_accounts" ("active");
CREATE INDEX IF NOT EXISTS "idx_telegram_li_merged__fd5216" ON "telegram_linked_accounts" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_telegram_li_id_tena_d7f0ee" ON "telegram_linked_accounts" ("id_tenant");
CREATE TABLE IF NOT EXISTS "telegram_lookups_message_sending_status" (
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
    CONSTRAINT "uid_telegram_lo_id_tena_a5309f" UNIQUE ("id_tenant", "code")
);
CREATE INDEX IF NOT EXISTS "idx_telegram_lo_touched_8a840d" ON "telegram_lookups_message_sending_status" ("touched");
CREATE INDEX IF NOT EXISTS "idx_telegram_lo_active_82c782" ON "telegram_lookups_message_sending_status" ("active");
CREATE INDEX IF NOT EXISTS "idx_telegram_lo_merged__1673c6" ON "telegram_lookups_message_sending_status" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_telegram_lo_id_tena_e281cb" ON "telegram_lookups_message_sending_status" ("id_tenant");
CREATE TABLE IF NOT EXISTS "telegram_options" (
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
    CONSTRAINT "uid_telegram_op_id_tena_36981a" UNIQUE ("id_tenant", "key")
);
CREATE INDEX IF NOT EXISTS "idx_telegram_op_touched_37306d" ON "telegram_options" ("touched");
CREATE INDEX IF NOT EXISTS "idx_telegram_op_active_5398bd" ON "telegram_options" ("active");
CREATE INDEX IF NOT EXISTS "idx_telegram_op_merged__63bcee" ON "telegram_options" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_telegram_op_id_tena_4b3f8d" ON "telegram_options" ("id_tenant");
CREATE TABLE IF NOT EXISTS "telegram_messages" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "receivers_telegram_id" BIGINT NOT NULL,
    "message_body" TEXT NOT NULL,
    "sent" TIMESTAMPTZ,
    "note" TEXT,
    "status_id" UUID REFERENCES "telegram_lookups_message_sending_status" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_telegram_me_touched_92c6c2" ON "telegram_messages" ("touched");
CREATE INDEX IF NOT EXISTS "idx_telegram_me_active_ba01da" ON "telegram_messages" ("active");
CREATE INDEX IF NOT EXISTS "idx_telegram_me_merged__8b5539" ON "telegram_messages" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_telegram_me_id_tena_54e849" ON "telegram_messages" ("id_tenant");
CREATE INDEX IF NOT EXISTS "idx_telegram_me_status__cddda7" ON "telegram_messages" ("status_id");
CREATE TABLE IF NOT EXISTS "telegram_messages_retry" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "scheduled_on" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "retries_left" SMALLINT NOT NULL  DEFAULT 5,
    "message_id" UUID NOT NULL REFERENCES "telegram_messages" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_telegram_me_schedul_cbe65c" ON "telegram_messages_retry" ("scheduled_on");
CREATE TABLE IF NOT EXISTS "telegram_translation_lookups_message_sending_status" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "lookup_id" UUID NOT NULL REFERENCES "telegram_lookups_message_sending_status" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_telegram_tr_lookup__0d29a5" ON "telegram_translation_lookups_message_sending_status" ("lookup_id");
