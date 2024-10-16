# Generated by Django 4.1.3 on 2022-12-22 10:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("sample", "0013_alter_standard_dilution_factor_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="slideimage",
            name="approved",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="slideimage",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="approved_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="slideimage",
            name="uploaded_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="uploaded_by",
                to=settings.AUTH_USER_MODEL,
                verbose_name="uploaded by",
            ),
        ),
    ]
