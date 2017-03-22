BEGIN;


-- next version: the column can be deleted for real

ALTER TABLE north_app_author
    DROP COLUMN date_of_birth;


COMMIT;
