\timing

BEGIN;


-- example of a manual migration


--meta-psql:do-until-0

with to_update as (
    SELECT
        id
    FROM north_app_book
    WHERE num_pages = 0
    LIMIT 5000
)
UPDATE north_app_book SET num_pages = 42 WHERE id IN (
    SELECT id FROM to_update
);


--meta-psql:done


COMMIT;
