-- upgrade --
CREATE TABLE IF NOT EXISTS "sendmail_mail_queue" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "id_tenant" UUID NOT NULL,
    "sender_email" VARCHAR(128) NOT NULL,
    "sender_display_name" VARCHAR(255),
    "receiver_email" VARCHAR(128) NOT NULL,
    "receiver_display_name" VARCHAR(255),
    "cc_receivers_list" JSONB,
    "bcc_receivers_list" JSONB,
    "subject" TEXT,
    "body" TEXT,
    "html_body" TEXT,
    "status" JSONB,
    "sent_to_gateway" TIMESTAMPTZ,
    "read_by_user" TIMESTAMPTZ,
    "attachments" JSONB
);
CREATE INDEX IF NOT EXISTS "idx_sendmail_ma_touched_21377d" ON "sendmail_mail_queue" ("touched");
CREATE INDEX IF NOT EXISTS "idx_sendmail_ma_active_e824cf" ON "sendmail_mail_queue" ("active");
CREATE INDEX IF NOT EXISTS "idx_sendmail_ma_merged__c0284d" ON "sendmail_mail_queue" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_sendmail_ma_id_tena_adcde6" ON "sendmail_mail_queue" ("id_tenant");
CREATE TABLE IF NOT EXISTS "sendmail_options" (
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
    CONSTRAINT "uid_sendmail_op_id_tena_ac4fbd" UNIQUE ("id_tenant", "key")
);
CREATE INDEX IF NOT EXISTS "idx_sendmail_op_touched_017afd" ON "sendmail_options" ("touched");
CREATE INDEX IF NOT EXISTS "idx_sendmail_op_active_34175a" ON "sendmail_options" ("active");
CREATE INDEX IF NOT EXISTS "idx_sendmail_op_merged__05a0f7" ON "sendmail_options" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_sendmail_op_id_tena_00dd12" ON "sendmail_options" ("id_tenant");
