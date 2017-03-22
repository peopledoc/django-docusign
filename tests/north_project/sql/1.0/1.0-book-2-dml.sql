BEGIN;


-- Add Book fixtures: contenttype & permissions

INSERT INTO django_content_type(app_label, model) VALUES('north_app', 'book');

INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_book', 'Can add book', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'book'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_book', 'Can change book', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'book'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_book', 'Can delete book', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'book'));


COMMIT;
