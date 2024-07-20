# Generated by Django 5.0.6 on 2024-07-20 08:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0003_alter_field_accepted_alter_field_options"),
        ("live", "0013_alter_socialuser_username_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="skeleton",
            name="instance",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="skeletons",
                to="live.instance",
            ),
        ),
    ]