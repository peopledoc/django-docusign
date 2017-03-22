BEGIN;


-- Create the Author table

CREATE TABLE "north_app_author" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "date_of_birth" date NOT NULL
)
;


COMMIT;
