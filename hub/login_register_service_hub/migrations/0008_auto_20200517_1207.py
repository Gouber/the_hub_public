# Generated by Django 3.0.6 on 2020-05-17 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_register_service_hub', '0007_auto_20200124_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
