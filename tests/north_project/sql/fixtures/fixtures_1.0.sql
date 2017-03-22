BEGIN;

INSERT INTO "django_site" (
    "id",
    "domain",
    "name"
) VALUES (
    1,
    'example.com',
    'example.com'
);
ALTER SEQUENCE django_site_id_seq RESTART WITH 2;

INSERT INTO django_content_type(app_label, model) VALUES('auth', 'group');
INSERT INTO django_content_type(app_label, model) VALUES('auth', 'user');
INSERT INTO django_content_type(app_label, model) VALUES('auth', 'permission');
INSERT INTO django_content_type(app_label, model) VALUES('contenttypes', 'contenttype');
INSERT INTO django_content_type(app_label, model) VALUES('sites', 'site');
INSERT INTO django_content_type(app_label, model) VALUES('north_app', 'author');
INSERT INTO django_content_type(app_label, model) VALUES('north_app', 'book');

INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_permission', 'Can add permission', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'permission'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_permission', 'Can change permission', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'permission'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_permission', 'Can delete permission', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'permission'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_group', 'Can add group', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'group'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_group', 'Can change group', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'group'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_group', 'Can delete group', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'group'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_user', 'Can add user', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'user'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_user', 'Can change user', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'user'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_user', 'Can delete user', (SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'user'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_contenttype', 'Can add content type', (SELECT id FROM django_content_type WHERE app_label = 'contenttypes' AND model = 'contenttype'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_contenttype', 'Can change content type', (SELECT id FROM django_content_type WHERE app_label = 'contenttypes' AND model = 'contenttype'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_contenttype', 'Can delete content type', (SELECT id FROM django_content_type WHERE app_label = 'contenttypes' AND model = 'contenttype'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_site', 'Can add site', (SELECT id FROM django_content_type WHERE app_label = 'sites' AND model = 'site'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_site', 'Can change site', (SELECT id FROM django_content_type WHERE app_label = 'sites' AND model = 'site'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_site', 'Can delete site', (SELECT id FROM django_content_type WHERE app_label = 'sites' AND model = 'site'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_author', 'Can add author', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'author'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_author', 'Can change author', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'author'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_author', 'Can delete author', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'author'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('add_book', 'Can add book', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'book'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('change_book', 'Can change book', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'book'));
INSERT INTO auth_permission(codename, name, content_type_id) VALUES('delete_book', 'Can delete book', (SELECT id FROM django_content_type WHERE app_label = 'north_app' AND model = 'book'));

COMMIT;
