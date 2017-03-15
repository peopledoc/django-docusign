import os

from django.core.exceptions import ImproperlyConfigured
from django.db.utils import ProgrammingError

import pytest

from django_north.management import migrations


def test_get_known_versions(settings):
    # wrong path
    settings.NORTH_MIGRATIONS_ROOT = '/path/to/nowhere'
    with pytest.raises(ImproperlyConfigured) as e:
        migrations.get_known_versions()
    assert (
        'settings.NORTH_MIGRATIONS_ROOT is improperly configured.' in e.value)

    root = os.path.dirname(__file__)
    settings.NORTH_MIGRATIONS_ROOT = os.path.join(root, 'foo')
    with pytest.raises(ImproperlyConfigured) as e:
        migrations.get_known_versions()
    assert (
        'settings.NORTH_MIGRATIONS_ROOT is improperly configured.' in e.value)

    # correct path
    settings.NORTH_MIGRATIONS_ROOT = os.path.join(root, 'data/project')
    result = migrations.get_known_versions()
    assert result == ['16.9', '16.11', '16.12', '17.01', '17.02', '17.3']


def test_get_current_version(mocker):
    cursor = mocker.MagicMock()
    mock_cursor = mocker.patch('django.db.connection.cursor')
    mock_cursor.return_value.__enter__.return_value = cursor

    # table does not exist
    cursor.execute.side_effect = ProgrammingError
    assert migrations.get_current_version() is None

    cursor.execute.side_effect = None

    # no comment
    cursor.fetchone.return_value = [None]
    with pytest.raises(migrations.DBException) as e:
        migrations.get_current_version()
    assert 'No comment found on django_site.' in e.value

    # bad comment
    cursor.fetchone.return_value = ['comment']
    with pytest.raises(migrations.DBException) as e:
        migrations.get_current_version()
    assert "No version found in django_site's comment." in e.value
    cursor.fetchone.return_value = ['version']
    with pytest.raises(migrations.DBException) as e:
        migrations.get_current_version()
    assert "No version found in django_site's comment." in e.value
    cursor.fetchone.return_value = ['version17.01']
    with pytest.raises(migrations.DBException) as e:
        migrations.get_current_version()
    assert "No version found in django_site's comment." in e.value

    # correct comment
    cursor.fetchone.return_value = [' version  17.01 ']
    assert migrations.get_current_version() == '17.01'


def test_get_migrations_to_apply(settings):
    root = os.path.dirname(__file__)
    settings.NORTH_MIGRATIONS_ROOT = os.path.join(root, 'data/project')

    # version folder does not exist
    with pytest.raises(migrations.DBException) as e:
        migrations.get_migrations_to_apply('foo')
    assert 'No sql folder found for version foo.' in e.value

    # no manual folder
    result = migrations.get_migrations_to_apply('17.02')
    migs = ['17.02-0-version-dml.sql', '17.02-feature_a-ddl.sql']
    assert result == {
        mig: os.path.join(
            settings.NORTH_MIGRATIONS_ROOT, '17.02', mig) for mig in migs
    }

    # with manual folder
    result = migrations.get_migrations_to_apply('17.01')
    migs = [
        '17.01-0-version-dml.sql',
        '17.01-feature_a-010-ddl.sql',
        '17.01-feature_a-020-ddl.sql',
        '17.01-feature_a-030-dml.sql',
        '17.01-feature_a-050-ddl.sql',
        '17.01-feature_b-ddl.sql',
    ]
    migration_dict = {
        mig: os.path.join(
            settings.NORTH_MIGRATIONS_ROOT, '17.01', mig) for mig in migs
    }
    migs = ['17.01-feature_a-040-dml.sql']
    migration_dict.update({
        mig: os.path.join(settings.NORTH_MIGRATIONS_ROOT, '17.01/manual', mig)
        for mig in migs
    })
    assert result == migration_dict


def test_build_migration_plan(settings, mocker):
    root = os.path.dirname(__file__)
    settings.NORTH_MIGRATIONS_ROOT = os.path.join(root, 'data/project')
    settings.NORTH_TARGET_VERSION = '17.02'

    mock_get_applied_versions = mocker.patch(
        'django_north.management.migrations.get_applied_versions')
    mock_get_current_version = mocker.patch(
        'django_north.management.migrations.get_current_version')
    mock_get_applied_migrations = mocker.patch(
        'django_north.management.migrations.get_applied_migrations')
    mocker.patch(
        'django_north.management.migrations.get_known_versions',
        return_value=['16.11', '16.12', '17.01', '17.02'])

    plan1612 = {
        'version': '16.12',
        'plan': [],
    }
    migs = ['16.12-0-version-dml.sql']
    plan1612['plan'] += [
        (mig, True, os.path.join(settings.NORTH_MIGRATIONS_ROOT, '16.12', mig))
        for mig in migs
    ]
    plan1701 = {
        'version': '17.01',
        'plan': [],
    }
    migs = [
        '17.01-0-version-dml.sql',
        '17.01-feature_a-010-ddl.sql',
        '17.01-feature_a-020-ddl.sql',
        '17.01-feature_a-030-dml.sql',
    ]
    plan1701['plan'] += [
        (mig, False, os.path.join(
            settings.NORTH_MIGRATIONS_ROOT, '17.01', mig))
        for mig in migs
    ]
    migs = ['17.01-feature_a-040-dml.sql']
    plan1701['plan'] += [
        (mig, False, os.path.join(
            settings.NORTH_MIGRATIONS_ROOT, '17.01/manual', mig))
        for mig in migs
    ]
    migs = [
        '17.01-feature_a-050-ddl.sql',
        '17.01-feature_b-ddl.sql',
    ]
    plan1701['plan'] += [
        (mig, False, os.path.join(
            settings.NORTH_MIGRATIONS_ROOT, '17.01', mig))
        for mig in migs
    ]
    plan1702 = {
        'version': '17.02',
        'plan': [],
    }
    migs = [
        '17.02-0-version-dml.sql',
        '17.02-feature_a-ddl.sql',
    ]
    plan1702['plan'] += [
        (mig, False, os.path.join(
            settings.NORTH_MIGRATIONS_ROOT, '17.02', mig))
        for mig in migs
    ]

    # applied versions are empty
    mock_get_applied_versions.return_value = []
    # applied migrations too
    mock_get_applied_migrations.return_value = []

    # current version is None
    mock_get_current_version.return_value = None
    result = migrations.build_migration_plan()
    assert result is None

    # current version is not None
    mock_get_current_version.return_value = '16.12'
    result = migrations.build_migration_plan()
    assert result['current_version'] == '16.12'
    assert result['init_version'] == '16.12'
    assert len(result['plans']) == 2
    assert result['plans'][0] == plan1701
    assert result['plans'][1] == plan1702

    # current version is out of scope
    mock_get_current_version.return_value = 'foo'
    with pytest.raises(migrations.DBException) as e:
        migrations.build_migration_plan()
    assert 'The current version of the database is unknown: foo.' in e.value

    # current version is the last one
    mock_get_current_version.return_value = '17.02'
    result = migrations.build_migration_plan()
    assert result['current_version'] == '17.02'
    assert result['init_version'] == '17.02'
    assert len(result['plans']) == 0

    mock_get_current_version.return_value = '16.12'

    # target version is out of scope
    settings.NORTH_TARGET_VERSION = 'foo'
    with pytest.raises(ImproperlyConfigured) as e:
        migrations.build_migration_plan()
    assert (
        'settings.NORTH_TARGET_VERSION is improperly configured: '
        'version foo not found.') in e.value

    settings.NORTH_TARGET_VERSION = '17.02'

    # applied versions are not empty
    mock_get_applied_versions.return_value = ['16.12']
    # applied migrations
    mock_get_applied_migrations.side_effect = [
        ['16.12-0-version-dml.sql'],
        [],
        [],
    ]
    result = migrations.build_migration_plan()
    assert result['current_version'] == '16.12'
    assert result['init_version'] == '16.11'
    assert len(result['plans']) == 3
    assert result['plans'][0] == plan1612
    assert result['plans'][1] == plan1701
    assert result['plans'][2] == plan1702

    # current version is the last one
    mock_get_current_version.return_value = '17.02'
    # applied versions are not empty
    mock_get_applied_versions.return_value = ['17.02']
    # applied migrations
    mock_get_applied_migrations.side_effect = [
        [],
    ]
    result = migrations.build_migration_plan()
    assert result['current_version'] == '17.02'
    assert result['init_version'] == '17.01'
    assert len(result['plans']) == 1
    assert result['plans'][0] == plan1702

    # applied versions are not empty
    mock_get_applied_versions.return_value = ['17.01', '17.02']
    # applied migrations
    mock_get_applied_migrations.side_effect = [
        [],
        [],
    ]
    result = migrations.build_migration_plan()
    assert result['current_version'] == '17.02'
    assert result['init_version'] == '16.12'
    assert len(result['plans']) == 2
    assert result['plans'][0] == plan1701
    assert result['plans'][1] == plan1702

    # target version is not the last one
    settings.NORTH_TARGET_VERSION = '17.01'
    # current version is not the last one
    mock_get_current_version.return_value = '16.12'
    # applied versions are not empty
    mock_get_applied_versions.return_value = ['16.12', '17.01']
    # applied migrations
    mock_get_applied_migrations.side_effect = [
        ['16.12-0-version-dml.sql'],
        [],
    ]
    result = migrations.build_migration_plan()
    assert result['current_version'] == '16.12'
    assert result['init_version'] == '16.11'
    assert len(result['plans']) == 2
    assert result['plans'][0] == plan1612
    assert result['plans'][1] == plan1701

    # edge case: current version > target version
    mock_get_current_version.return_value = '17.02'
    # applied versions are not empty
    mock_get_applied_versions.return_value = ['16.12', '17.01', '17.02']
    # applied migrations
    mock_get_applied_migrations.side_effect = [
        ['16.12-0-version-dml.sql'],
        [],
        [],
    ]
    result = migrations.build_migration_plan()
    assert result['current_version'] == '17.02'
    assert result['init_version'] == '16.11'
    assert len(result['plans']) == 2
    assert result['plans'][0] == plan1612
    assert result['plans'][1] == plan1701


def test_get_version_for_init(settings, mocker):
    root = os.path.dirname(__file__)
    settings.NORTH_MIGRATIONS_ROOT = os.path.join(root, 'data/project')
    mock_versions = mocker.patch(
        'django_north.management.migrations.get_known_versions')

    mock_versions.return_value = ['16.11', '16.12', '17.01', '17.02']

    # target version is out of scope
    settings.NORTH_TARGET_VERSION = 'foo'
    with pytest.raises(ImproperlyConfigured) as e:
        migrations.get_version_for_init()
    assert (
        'settings.NORTH_TARGET_VERSION is improperly configured: '
        'version foo not found.') in e.value

    # schema for the version exists
    settings.NORTH_TARGET_VERSION = '17.02'
    assert migrations.get_version_for_init() == '17.02'

    # schema for the version does not exist, take the first ancestor
    settings.NORTH_TARGET_VERSION = '17.01'
    assert migrations.get_version_for_init() == '16.12'

    # no schema for the version, and no ancestors
    settings.NORTH_TARGET_VERSION = '16.11'
    with pytest.raises(migrations.DBException) as e:
        migrations.get_version_for_init()
    assert ('Can not find a schema to init the DB.') in e.value

    # no ancestors, but the schema exists
    mock_versions.return_value = ['16.12', '17.01', '17.02']
    settings.NORTH_TARGET_VERSION = '17.01'
    assert migrations.get_version_for_init() == '16.12'

    # wrong template
    settings.NORTH_SCHEMA_TPL = 'foo.sql'
    with pytest.raises(migrations.DBException) as e:
        migrations.get_version_for_init()
    assert ('Can not find a schema to init the DB.') in e.value
    settings.NORTH_SCHEMA_TPL = 'foo{}.sql'
    with pytest.raises(migrations.DBException) as e:
        migrations.get_version_for_init()
    assert ('Can not find a schema to init the DB.') in e.value
