from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='type',
            field=models.CharField(choices=[('Ambulance', 'Ambulance'), ('Police', 'Police'), ('Fire Truck', 'Fire Truck'), ('Technical', 'Technical')], max_length=50),
        ),
    ]



