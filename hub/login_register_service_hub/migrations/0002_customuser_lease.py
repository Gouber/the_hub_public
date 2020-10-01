# Generated by Django 3.0.1 on 2020-01-13 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('houses_hub', '0001_initial'),
        ('login_register_service_hub', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='lease',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='houses_hub.Lease'),
        ),
    ]