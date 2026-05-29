# Generated migration to backfill resource assignment data from legacy format

from django.db import migrations
import re


def backfill_resource_assignment(apps, schema_editor):
    """
    Parse existing Zasob.status field to extract incident assignment and
    populate new assigned_to FK and resource_status enum.

    Legacy format:
    - "Assigned to INC-{id}" -> assigned_to FK, resource_status='assigned'
    - dostepnosc=True, not assigned -> resource_status='available'
    - dostepnosc=False, not assigned -> resource_status='unavailable'
    """

    Zasob = apps.get_model('management', 'Zasob')
    Incydent = apps.get_model('management', 'Incydent')

    pattern = re.compile(r'Assigned to INC-(\d+)')

    for zasob in Zasob.objects.all():
        # Try to match the "Assigned to INC-{id}" pattern
        match = pattern.search(zasob.status or '')
        if match:
            try:
                incident_id = int(match.group(1))
                incident = Incydent.objects.get(id=incident_id)
                zasob.assigned_to = incident
                zasob.resource_status = 'assigned'
            except (Incydent.DoesNotExist, ValueError):
                # If incident no longer exists, mark as unavailable
                zasob.resource_status = 'unavailable'
        else:
            # No assignment pattern found; use dostepnosc to determine status
            if zasob.dostepnosc:
                zasob.resource_status = 'available'
            else:
                zasob.resource_status = 'unavailable'

        zasob.save()


def reverse_backfill(apps, schema_editor):
    """
    Reverse: restore old status format from assigned_to FK.
    For simplicity, just reset resource_status and assigned_to to defaults.
    """

    Zasob = apps.get_model('management', 'Zasob')

    for zasob in Zasob.objects.all():
        # Reverse: reconstruct old free-text status from FK if present
        if zasob.assigned_to:
            zasob.status = f"Assigned to INC-{zasob.assigned_to.id}"
        else:
            zasob.status = "Available"

        zasob.assigned_to = None
        zasob.resource_status = 'available'
        zasob.save()


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0008_expand_resource_assignment'),
    ]

    operations = [
        migrations.RunPython(backfill_resource_assignment, reverse_backfill),
    ]

