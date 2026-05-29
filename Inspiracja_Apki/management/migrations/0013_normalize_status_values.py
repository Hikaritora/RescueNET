from django.db import migrations


def normalize_statuses(apps, schema_editor):
    Incydent = apps.get_model('management', 'Incydent')
    for inc in Incydent.objects.all():
        s = (inc.status or '').strip()
        norm = s.lower().replace('-', '_').replace(' ', '_')
        if norm in ('reported', 'in_progress', 'closed'):
            if inc.status != norm:
                inc.status = norm
                inc.save()


def reverse_normalize(apps, schema_editor):
    # Can't reliably reverse; leave as-is
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0012_rename_fields_to_english'),
    ]

    operations = [
        migrations.RunPython(normalize_statuses, reverse_normalize),
    ]

