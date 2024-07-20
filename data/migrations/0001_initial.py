# Generated by Django 5.0.6 on 2024-07-19 12:07

import django.db.models.deletion
import jsonfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Field",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("short-text", "Short answer text"),
                            ("long-text", "Long answer text"),
                            ("number", "Numeric answer"),
                            (
                                "multioption-singleanswer",
                                "Multiple choice single answer",
                            ),
                            (
                                "multioption-multianswer",
                                "Multiple choice multiple answers",
                            ),
                            ("file", "File upload"),
                        ],
                        max_length=255,
                    ),
                ),
                ("required", models.BooleanField(default=False)),
                ("options", jsonfield.fields.JSONField(blank=True, null=True)),
                ("accepted", jsonfield.fields.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Response",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Skeleton",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("endMessage", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.TextField()),
                (
                    "field",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data.field"
                    ),
                ),
                (
                    "response",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="data.response",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="response",
            name="skeleton",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="responses",
                to="data.skeleton",
            ),
        ),
        migrations.AddField(
            model_name="field",
            name="skeleton",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="fields",
                to="data.skeleton",
            ),
        ),
    ]