# Generated by Django 5.1 on 2024-08-20 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0013_project_shared_users_delete_projectshare'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_premium',
            field=models.BooleanField(default=False),
        ),
    ]