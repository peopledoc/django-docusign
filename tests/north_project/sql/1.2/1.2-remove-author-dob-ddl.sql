BEGIN;


-- The field Author.date_of_birth is removed from the code.
-- But as the sql field is not nullable, to have a blue/green sql migration,
-- we have to set it nullable first, and wait for a next version to remove it from the schema

ALTER TABLE north_app_author
    ALTER COLUMN date_of_birth DROP NOT NULL;


COMMIT;
