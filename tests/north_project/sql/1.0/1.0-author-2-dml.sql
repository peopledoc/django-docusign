BEGIN;


-- Add Author fixtures: contenttype & permissions

INSERT INTO django_content_type(app_label, model) VALUES('north_app', 'author');

INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_author', 'Can add author', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'author'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_author', 'Can change author', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'author'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_author', 'Can delete author', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'author'));


COMMIT;
