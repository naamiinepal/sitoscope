# Generated by Django 4.1.3 on 2024-06-05 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("annotation", "0006_annotation_unique_image_annotator_pair"),
    ]

    operations = [
        migrations.AddField(
            model_name="annotation",
            name="annotation_phase",
            field=models.CharField(max_length=200, null=True),
        ),
    ]
