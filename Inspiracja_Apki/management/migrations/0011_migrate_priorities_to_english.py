from django.db import migrations


def migrate_priorities(apps, schema_editor):
    Incydent = apps.get_model('management', 'Incydent')

    mapping = {
        'niski': 'low',
        'średni': 'medium',
        'wysoki': 'high',
        'krytyczny': 'critical',
    }

    for old, new in mapping.items():
        Incydent.objects.filter(priorytet=old).update(priorytet=new)


def reverse_migrate_priorities(apps, schema_editor):
    Incydent = apps.get_model('management', 'Incydent')

    reverse = {
        'low': 'niski',
        'medium': 'średni',
        'high': 'wysoki',
        'critical': 'krytyczny',
    }

    for new, old in reverse.items():
        Incydent.objects.filter(priorytet=new).update(priorytet=old)


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0010_contract_resource_legacy_fields'),
    ]

    operations = [
        migrations.RunPython(migrate_priorities, reverse_migrate_priorities),
    ]

