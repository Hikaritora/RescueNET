from django.db import migrations


def migrate_roles(apps, schema_editor):
    User = apps.get_model('management', 'Uzytkownik')
    mapping = {
        'dyspozytor': 'dispatcher',
        'ratownik': 'rescuer',
        'admin': 'admin',
    }
    for old, new in mapping.items():
        User.objects.filter(role=old).update(role=new)


def reverse_migrate_roles(apps, schema_editor):
    User = apps.get_model('management', 'Uzytkownik')
    reverse = {
        'dispatcher': 'dyspozytor',
        'rescuer': 'ratownik',
        'admin': 'admin',
    }
    for new, old in reverse.items():
        User.objects.filter(role=new).update(role=old)


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0013_normalize_status_values'),
    ]

    operations = [
        migrations.RunPython(migrate_roles, reverse_migrate_roles),
    ]

