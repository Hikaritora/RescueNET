# Generated migration to add resource assignment FK and status enum

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0007_convert_status_to_english'),
    ]

    operations = [
        # Add the resource_status field to store normalized status
        migrations.AddField(
            model_name='zasob',
            name='resource_status',
            field=models.CharField(
                choices=[
                    ('available', 'Available'),
                    ('assigned', 'Assigned'),
                    ('unavailable', 'Unavailable'),
                ],
                default='available',
                max_length=20,
            ),
        ),
        # Add the assigned_to FK to link resources directly to incidents
        migrations.AddField(
            model_name='zasob',
            name='assigned_to',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='management.incydent',
                related_name='assigned_resources',
            ),
        ),
    ]

