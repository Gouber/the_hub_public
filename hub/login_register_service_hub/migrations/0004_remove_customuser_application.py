# Generated by Django 3.0.1 on 2020-01-22 12:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login_register_service_hub', '0003_customuser_application'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='application',
        ),
    ]