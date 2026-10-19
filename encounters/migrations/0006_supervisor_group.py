from django.db import migrations


def create_supervisor_group(apps, schema_editor):
    # make sure the animal permissions exist before we look them up
    from django.contrib.auth.management import create_permissions
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group, created = Group.objects.get_or_create(name='Supervisor')
    perms = Permission.objects.filter(
        content_type__app_label='encounters',
        codename__in=['view_animal', 'change_animal'],
    )
    group.permissions.add(*perms)
    print('\n  Supervisor group ready. In the admin, give a user "Staff status"'
          ' and add them to the Supervisor group so they can mark animals inactive.')


class Migration(migrations.Migration):

    dependencies = [
        ('encounters', '0005_encounter_participation'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(create_supervisor_group, migrations.RunPython.noop),
    ]
