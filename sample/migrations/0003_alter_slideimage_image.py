# Generated by Django 4.1.3 on 2022-11-28 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sample", "0002_alter_slideimage_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="slideimage",
            name="image",
            field=models.ImageField(
                upload_to="upload_samples", verbose_name="Slide Image"
            ),
        ),
    ]
