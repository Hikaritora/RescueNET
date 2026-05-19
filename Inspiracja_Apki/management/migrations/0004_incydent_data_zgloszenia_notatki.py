from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0003_zasob_lat_zasob_lng_alter_zasob_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='incydent',
            name='data_zgloszenia',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='incydent',
            name='notatki',
            field=models.TextField(blank=True, default=''),
        ),
    ]
