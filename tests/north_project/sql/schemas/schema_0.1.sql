-- Init version table --

CREATE TABLE sql_version (
    version_num text UNIQUE NOT NULL
)
;

-- Init django tables --

CREATE TABLE "auth_permission" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    "content_type_id" integer NOT NULL,
    "codename" varchar(100) NOT NULL,
    UNIQUE ("content_type_id", "codename")
)
;
CREATE TABLE "auth_group_permissions" (
    "id" serial NOT NULL PRIMARY KEY,
    "group_id" integer NOT NULL,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("group_id", "permission_id")
)
;
CREATE TABLE "auth_group" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL UNIQUE
)
;
ALTER TABLE "auth_group_permissions" ADD CONSTRAINT "group_id_refs_id_f4b32aac" FOREIGN KEY ("group_id") REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "auth_user_groups" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "group_id")
)
;
CREATE TABLE "auth_user_user_permissions" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "permission_id")
)
;
CREATE TABLE "auth_user" (
    "id" serial NOT NULL PRIMARY KEY,
    "password" varchar(128) NOT NULL,
    "last_login" timestamp with time zone,
    "is_superuser" boolean NOT NULL,
    "username" varchar(30) NOT NULL UNIQUE,
    "first_name" varchar(30) NOT NULL,
    "last_name" varchar(30) NOT NULL,
    "email" varchar(254) NOT NULL,
    "is_staff" boolean NOT NULL,
    "is_active" boolean NOT NULL,
    "date_joined" timestamp with time zone NOT NULL
)
;
ALTER TABLE "auth_user_groups" ADD CONSTRAINT "user_id_refs_id_40c41112" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "auth_user_user_permissions" ADD CONSTRAINT "user_id_refs_id_4dc23c39" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
-- The following references should be added but depend on non-existent tables:
-- ALTER TABLE "auth_permission" ADD CONSTRAINT "content_type_id_refs_id_d043b34a" FOREIGN KEY ("content_type_id") REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "auth_permission_content_type_id" ON "auth_permission" ("content_type_id");
CREATE INDEX "auth_group_permissions_group_id" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id" ON "auth_group_permissions" ("permission_id");
CREATE INDEX "auth_group_name_like" ON "auth_group" ("name" varchar_pattern_ops);
CREATE INDEX "auth_user_groups_user_id" ON "auth_user_groups" ("user_id");
CREATE INDEX "auth_user_groups_group_id" ON "auth_user_groups" ("group_id");
CREATE INDEX "auth_user_user_permissions_user_id" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX "auth_user_user_permissions_permission_id" ON "auth_user_user_permissions" ("permission_id");
CREATE INDEX "auth_user_username_like" ON "auth_user" ("username" varchar_pattern_ops);

CREATE TABLE "django_content_type" (
    "id" serial NOT NULL PRIMARY KEY,
    "app_label" varchar(100) NOT NULL,
    "model" varchar(100) NOT NULL,
    UNIQUE ("app_label", "model")
)
;

CREATE TABLE "django_site" (
    "id" serial NOT NULL PRIMARY KEY,
    "domain" varchar(100) NOT NULL,
    "name" varchar(50) NOT NULL
)
;

CREATE TABLE django_migrations (
    "id" serial NOT NULL PRIMARY KEY,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);
