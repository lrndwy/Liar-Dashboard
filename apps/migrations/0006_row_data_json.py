# Generated by Django 5.0.6 on 2024-08-15 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0005_remove_data_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='row',
            name='data_json',
            field=models.JSONField(default=dict),
        ),
    ]