BEGIN;


-- Add a new field num_pages on Book model, with a default

ALTER TABLE north_app_book ADD COLUMN "num_pages" integer DEFAULT 0 NOT NULL;

COMMIT;
