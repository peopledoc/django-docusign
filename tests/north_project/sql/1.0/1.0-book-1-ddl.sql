BEGIN;


-- Create the Book table

CREATE TABLE "north_app_book" (
    "id" serial NOT NULL PRIMARY KEY,
    "author_id" integer NOT NULL REFERENCES "north_app_author" ("id") DEFERRABLE INITIALLY DEFERRED,
    "title" varchar(100) NOT NULL
)
;
CREATE INDEX "north_app_book_author_id" ON "north_app_book" ("author_id");


COMMIT;
