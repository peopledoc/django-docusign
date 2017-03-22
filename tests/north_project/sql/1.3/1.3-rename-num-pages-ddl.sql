BEGIN;


-- Remove compatibility view for N-1 code

DROP VIEW north_app_book;
ALTER TABLE north_app_book_wip RENAME TO north_app_book;


COMMIT;
