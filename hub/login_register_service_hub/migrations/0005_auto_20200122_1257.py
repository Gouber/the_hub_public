# Generated by Django 3.0.1 on 2020-01-22 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses_hub', '0003_auto_20200122_1232'),
        ('login_register_service_hub', '0004_remove_customuser_application'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='lease',
        ),
        migrations.AddField(
            model_name='customuser',
            name='lease',
            field=models.ManyToManyField(to='houses_hub.Lease'),
        ),
    ]
