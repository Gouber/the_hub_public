# Generated by Django 3.0.1 on 2020-01-24 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses_hub', '0004_auto_20200123_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='submitted',
            field=models.BooleanField(default=False),
        ),
    ]
