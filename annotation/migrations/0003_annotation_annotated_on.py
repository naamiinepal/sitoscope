# Generated by Django 4.1.3 on 2023-03-27 05:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("annotation", "0002_annotation"),
    ]

    operations = [
        migrations.AddField(
            model_name="annotation",
            name="annotated_on",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
