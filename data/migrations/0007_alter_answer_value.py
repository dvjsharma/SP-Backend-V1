# Generated by Django 5.0.6 on 2024-08-08 06:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0006_response_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="answer",
            name="value",
            field=models.JSONField(blank=True, null=True),
        ),
    ]