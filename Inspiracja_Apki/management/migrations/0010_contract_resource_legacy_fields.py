# Generated migration to remove legacy fields and finalize resource_status

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0009_backfill_resource_assignment_data'),
    ]

    operations = [
        # Remove legacy dostepnosc field (no longer needed)
        migrations.RemoveField(
            model_name='zasob',
            name='dostepnosc',
        ),
        # Remove legacy free-text status field
        migrations.RemoveField(
            model_name='zasob',
            name='status',
        ),
        # Rename resource_status -> status to finalize the field name
        migrations.RenameField(
            model_name='zasob',
            old_name='resource_status',
            new_name='status',
        ),
        # Add a database index on the new status field for query performance
        migrations.AddIndex(
            model_name='zasob',
            index=models.Index(fields=['status'], name='management_zasob_status_idx'),
        ),
        # Optional: add unique constraint on name for easier lookup
        migrations.AlterField(
            model_name='zasob',
            name='nazwa',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]

