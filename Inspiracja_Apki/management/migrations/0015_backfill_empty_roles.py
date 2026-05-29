from django.db import migrations


def set_default_rescuer(apps, schema_editor):
    User = apps.get_model('management', 'Uzytkownik')
    # Backfill empty-string roles and NULL roles to 'rescuer'.
    User.objects.filter(role='').update(role='rescuer')
    User.objects.filter(role__isnull=True).update(role='rescuer')


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0014_migrate_roles_to_english'),
    ]

    operations = [
        # reverse is noop to avoid accidentally reverting legitimate 'rescuer' values
        migrations.RunPython(set_default_rescuer, reverse_code=migrations.RunPython.noop),
    ]

