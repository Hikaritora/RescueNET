from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0011_migrate_priorities_to_english'),
    ]

    operations = [
        # Rename Incydent fields to English
        migrations.RenameField(
            model_name='incydent',
            old_name='typ',
            new_name='type',
        ),
        migrations.RenameField(
            model_name='incydent',
            old_name='lat',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='incydent',
            old_name='lng',
            new_name='longitude',
        ),
        migrations.RenameField(
            model_name='incydent',
            old_name='priorytet',
            new_name='priority',
        ),
        migrations.RenameField(
            model_name='incydent',
            old_name='zglaszajacy',
            new_name='reporter',
        ),
        migrations.RenameField(
            model_name='incydent',
            old_name='data_zgloszenia',
            new_name='reported_at',
        ),
        migrations.RenameField(
            model_name='incydent',
            old_name='notatki',
            new_name='notes',
        ),
        # Rename Zasob fields to English
        migrations.RenameField(
            model_name='zasob',
            old_name='nazwa',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='zasob',
            old_name='typ',
            new_name='type',
        ),
        migrations.RenameField(
            model_name='zasob',
            old_name='specjalizacja',
            new_name='specialization',
        ),
        migrations.RenameField(
            model_name='zasob',
            old_name='lat',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='zasob',
            old_name='lng',
            new_name='longitude',
        ),
        # Rename Uzytkownik field to English
        migrations.RenameField(
            model_name='uzytkownik',
            old_name='rola',
            new_name='role',
        ),
    ]

