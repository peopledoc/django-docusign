BEGIN;


-- The field num_pages is remaned into pages

-- Rename the column
ALTER TABLE north_app_book RENAME COLUMN num_pages TO pages;

-- Create compatibility view for N-1 code
ALTER TABLE north_app_book RENAME TO north_app_book_wip;
CREATE VIEW north_app_book AS SELECT *, pages AS num_pages FROM north_app_book_wip;


COMMIT;
