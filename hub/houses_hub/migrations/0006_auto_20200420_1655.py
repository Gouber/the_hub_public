# Generated by Django 3.0.5 on 2020-04-20 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses_hub', '0005_application_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='lat',
            field=models.DecimalField(decimal_places=12, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='house',
            name='lgn',
            field=models.DecimalField(decimal_places=12, max_digits=15, null=True),
        ),
    ]
