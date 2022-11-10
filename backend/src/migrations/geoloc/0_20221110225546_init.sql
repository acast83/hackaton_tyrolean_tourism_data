-- upgrade --
CREATE TABLE IF NOT EXISTS "geoloc_countries" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "code" VARCHAR(32) NOT NULL UNIQUE,
    "en_value" VARCHAR(128) NOT NULL UNIQUE,
    "local_value" VARCHAR(128) NOT NULL UNIQUE,
    "eu_country" BOOL
);
CREATE INDEX IF NOT EXISTS "idx_geoloc_coun_touched_b98d27" ON "geoloc_countries" ("touched");
CREATE INDEX IF NOT EXISTS "idx_geoloc_coun_active_1111b3" ON "geoloc_countries" ("active");
CREATE INDEX IF NOT EXISTS "idx_geoloc_coun_merged__ddefdd" ON "geoloc_countries" ("merged_with");
CREATE TABLE IF NOT EXISTS "geoloc_options" (
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
    CONSTRAINT "uid_geoloc_opti_id_tena_bf4f90" UNIQUE ("id_tenant", "key")
);
CREATE INDEX IF NOT EXISTS "idx_geoloc_opti_touched_dabe22" ON "geoloc_options" ("touched");
CREATE INDEX IF NOT EXISTS "idx_geoloc_opti_active_96603a" ON "geoloc_options" ("active");
CREATE INDEX IF NOT EXISTS "idx_geoloc_opti_merged__99df1d" ON "geoloc_options" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_geoloc_opti_id_tena_0e1a75" ON "geoloc_options" ("id_tenant");
CREATE TABLE IF NOT EXISTS "geoloc_regions" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "local_value" VARCHAR(128) NOT NULL,
    "cs_value" VARCHAR(128),
    "en_value" VARCHAR(128),
    "country_id" UUID NOT NULL REFERENCES "geoloc_countries" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_geoloc_regi_country_c8d126" UNIQUE ("country_id", "local_value")
);
CREATE INDEX IF NOT EXISTS "idx_geoloc_regi_touched_a09ebd" ON "geoloc_regions" ("touched");
CREATE INDEX IF NOT EXISTS "idx_geoloc_regi_active_a0010d" ON "geoloc_regions" ("active");
CREATE INDEX IF NOT EXISTS "idx_geoloc_regi_merged__e4dc7a" ON "geoloc_regions" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_geoloc_regi_country_f53af4" ON "geoloc_regions" ("country_id");
CREATE TABLE IF NOT EXISTS "geoloc_provinces" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "local_value" VARCHAR(128) NOT NULL,
    "cs_value" VARCHAR(128),
    "en_value" VARCHAR(128),
    "code" VARCHAR(32),
    "country_id" UUID NOT NULL REFERENCES "geoloc_countries" ("id") ON DELETE CASCADE,
    "region_id" UUID REFERENCES "geoloc_regions" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_geoloc_prov_country_578b84" UNIQUE ("country_id", "local_value"),
    CONSTRAINT "uid_geoloc_prov_country_6c0fe5" UNIQUE ("country_id", "code"),
    CONSTRAINT "uid_geoloc_prov_region__c7f265" UNIQUE ("region_id", "local_value")
);
CREATE INDEX IF NOT EXISTS "idx_geoloc_prov_touched_8bbd10" ON "geoloc_provinces" ("touched");
CREATE INDEX IF NOT EXISTS "idx_geoloc_prov_active_f1e00e" ON "geoloc_provinces" ("active");
CREATE INDEX IF NOT EXISTS "idx_geoloc_prov_merged__1308f6" ON "geoloc_provinces" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_geoloc_prov_country_dd2b27" ON "geoloc_provinces" ("country_id");
CREATE INDEX IF NOT EXISTS "idx_geoloc_prov_region__47a058" ON "geoloc_provinces" ("region_id");
CREATE TABLE IF NOT EXISTS "geoloc_municipalities" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "zip" VARCHAR(32),
    "istat_code" VARCHAR(32),
    "local_value" VARCHAR(128) NOT NULL,
    "cs_value" VARCHAR(128),
    "en_value" VARCHAR(128),
    "country_id" UUID NOT NULL REFERENCES "geoloc_countries" ("id") ON DELETE CASCADE,
    "province_id" UUID REFERENCES "geoloc_provinces" ("id") ON DELETE CASCADE,
    "region_id" UUID REFERENCES "geoloc_regions" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_geoloc_muni_country_e6056b" UNIQUE ("country_id", "zip", "local_value"),
    CONSTRAINT "uid_geoloc_muni_region__89f1af" UNIQUE ("region_id", "zip", "local_value"),
    CONSTRAINT "uid_geoloc_muni_provinc_739078" UNIQUE ("province_id", "zip", "local_value")
);
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_touched_7186fd" ON "geoloc_municipalities" ("touched");
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_active_5b351b" ON "geoloc_municipalities" ("active");
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_merged__e5e226" ON "geoloc_municipalities" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_zip_2f0e21" ON "geoloc_municipalities" ("zip");
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_istat_c_646823" ON "geoloc_municipalities" ("istat_code");
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_country_9d1cdb" ON "geoloc_municipalities" ("country_id");
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_provinc_3fdadc" ON "geoloc_municipalities" ("province_id");
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_region__09f49a" ON "geoloc_municipalities" ("region_id");
CREATE TABLE IF NOT EXISTS "geoloc_municipalities_search" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "municipality_id" UUID NOT NULL REFERENCES "geoloc_municipalities" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_touched_1f994d" ON "geoloc_municipalities_search" ("touched");
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_active_e74485" ON "geoloc_municipalities_search" ("active");
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_merged__da96df" ON "geoloc_municipalities_search" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_geoloc_muni_municip_9ab47e" ON "geoloc_municipalities_search" ("municipality_id");
CREATE TABLE IF NOT EXISTS "geoloc_translations_countries" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "cs_value" TEXT,
    "country_id" UUID NOT NULL REFERENCES "geoloc_countries" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_touched_ef014b" ON "geoloc_translations_countries" ("touched");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_active_6d3108" ON "geoloc_translations_countries" ("active");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_merged__cd7e6c" ON "geoloc_translations_countries" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_country_7749fa" ON "geoloc_translations_countries" ("country_id");
CREATE TABLE IF NOT EXISTS "geoloc_translations_municipalities" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "cs_value" TEXT,
    "municipality_id" UUID NOT NULL REFERENCES "geoloc_municipalities" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_touched_4491f8" ON "geoloc_translations_municipalities" ("touched");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_active_3960c2" ON "geoloc_translations_municipalities" ("active");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_merged__d5d01d" ON "geoloc_translations_municipalities" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_municip_93dd36" ON "geoloc_translations_municipalities" ("municipality_id");
CREATE TABLE IF NOT EXISTS "geoloc_translations_provinces" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "cs_value" TEXT,
    "province_id" UUID NOT NULL REFERENCES "geoloc_provinces" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_touched_01dc5a" ON "geoloc_translations_provinces" ("touched");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_active_e19f83" ON "geoloc_translations_provinces" ("active");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_merged__b0beb2" ON "geoloc_translations_provinces" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_provinc_00fb33" ON "geoloc_translations_provinces" ("province_id");
CREATE TABLE IF NOT EXISTS "geoloc_translations_regions" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "last_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_updated_by" UUID NOT NULL,
    "touched" BOOL NOT NULL  DEFAULT False,
    "active" BOOL   DEFAULT True,
    "merged_with" UUID,
    "language" VARCHAR(32) NOT NULL,
    "value" TEXT NOT NULL,
    "cs_value" TEXT,
    "region_id" UUID NOT NULL REFERENCES "geoloc_regions" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_touched_0cb301" ON "geoloc_translations_regions" ("touched");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_active_7fd22c" ON "geoloc_translations_regions" ("active");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_merged__5af658" ON "geoloc_translations_regions" ("merged_with");
CREATE INDEX IF NOT EXISTS "idx_geoloc_tran_region__c5f452" ON "geoloc_translations_regions" ("region_id");
