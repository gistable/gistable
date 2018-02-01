"""
Test (data) migrations in Django.

This uses py.test/pytest-django (the `transactional_db` fixture comes from there),
but could be easily adopted for Django's testrunner:

    from django.test.testcases import TransactionTestCase

    class FooTestcase(TransactionTestCase):
        def test_with_django(self):
        …

This example tests that some fields are properly migrated from a `Profile` model
to `User`.
"""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor


def test_migrate_profile_to_user(transactional_db):
    executor = MigrationExecutor(connection)
    app = "YOUR_APP"
    migrate_from = [(app, "000X_before")]
    migrate_to = [(app, "000X_after")]

    executor.migrate(migrate_from)
    old_apps = executor.loader.project_state(migrate_from).apps

    # Create some old data.
    Profile = old_apps.get_model(app, "Profile")
    old_profile = Profile.objects.create(email="email",
                                         firstname="firstname",
                                         lastname="lastname")
    # Migrate forwards.
    executor.loader.build_graph()  # reload.
    executor.migrate(migrate_to)
    new_apps = executor.loader.project_state(migrate_to).apps

    # Test the new data.
    Profile = new_apps.get_model(app, "Profile")
    User = new_apps.get_model(app, "UserEntry")
    assert 'firstname' not in Profile._meta.get_all_field_names()

    user = User.objects.get(email='email')
    profile = Profile.objects.get(user__email='email')
    assert user.profile.pk == old_profile.pk == profile.pk
    assert profile.user.email == 'email'
    assert profile.user.first_name == 'firstname'
    assert profile.user.last_name == 'lastname'
