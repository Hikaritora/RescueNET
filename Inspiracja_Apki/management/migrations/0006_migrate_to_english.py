from django.db import migrations


def migrate_to_english(apps, schema_editor):
    """Convert existing incident status values from Polish to English."""

    incident = apps.get_model('management', 'Incydent')

    status_mapping = {
        'zgłoszony': 'reported',
        'w toku': 'in_progress',
        'zakończony': 'closed',
    }

    for old_status, new_status in status_mapping.items():
        incident.objects.filter(status=old_status).update(status=new_status)


def reverse_migrate(apps, schema_editor):
    """Convert incident status values back to Polish if the migration is reversed."""

    incident = apps.get_model('management', 'Incydent')

    status_mapping_reverse = {
        'reported': 'zgłoszony',
        'in_progress': 'w toku',
        'closed': 'zakończony',
    }

    for new_status, old_status in status_mapping_reverse.items():
        incident.objects.filter(status=new_status).update(status=old_status)


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0005_alter_incydent_typ'),
    ]

    operations = [
        migrations.RunPython(migrate_to_english, reverse_migrate),
    ]

