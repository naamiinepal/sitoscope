# Generated by Django 4.1.3 on 2023-03-27 05:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sample", "0015_slideimage_annotated_slideimage_annotator"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="slideimage",
            name="annotated",
        ),
        migrations.RemoveField(
            model_name="slideimage",
            name="annotator",
        ),
    ]
