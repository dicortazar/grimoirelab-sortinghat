# Generated by Django 2.1 on 2020-04-20 12:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_uidentity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='individual',
            old_name='uuid',
            new_name='mk',
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='individual',
            field=models.ForeignKey(db_column='mk', on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='core.Individual', to_field='mk'),
        ),
        migrations.AlterField(
            model_name='identity',
            name='individual',
            field=models.ForeignKey(db_column='mk', on_delete=django.db.models.deletion.CASCADE, related_name='identities', to='core.Individual', to_field='mk'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='individual',
            field=models.OneToOneField(db_column='mk', on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='core.Individual', to_field='mk'),
        ),
    ]
