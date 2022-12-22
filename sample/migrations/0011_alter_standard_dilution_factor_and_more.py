# Generated by Django 4.1.3 on 2022-12-22 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sample", "0010_standard_sample_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="standard",
            name="dilution_factor",
            field=models.DecimalField(decimal_places=6, max_digits=10),
        ),
        migrations.AlterField(
            model_name="standard",
            name="expected_concentration",
            field=models.DecimalField(decimal_places=6, max_digits=10),
        ),
        migrations.AlterField(
            model_name="standard",
            name="observed_concentration",
            field=models.DecimalField(decimal_places=6, max_digits=10),
        ),
    ]
