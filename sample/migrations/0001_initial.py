# Generated by Django 4.1.3 on 2022-11-25 05:12

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        (
            "address",
            "0002_alter_district_province_alter_municipality_district_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Slide",
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
                (
                    "slide_number",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(3),
                        ]
                    ),
                ),
            ],
            options={
                "verbose_name": "slide",
            },
        ),
        migrations.CreateModel(
            name="Water",
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
                ("date_of_collection", models.DateField(default=datetime.date.today)),
                ("sample_id", models.CharField(max_length=500, unique=True)),
                ("site_image", models.ImageField(upload_to="site_images")),
                ("locality", models.CharField(max_length=500, null=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("RI", "River"),
                            ("MT", "Municipal Tap"),
                            ("BO", "Bottled"),
                            ("JA", "Jar"),
                            ("LA", "Lake"),
                            ("TA", "Tanker"),
                            ("TU", "Tubewell"),
                            ("SW", "Spring Water"),
                        ],
                        max_length=2,
                    ),
                ),
                ("use", models.CharField(max_length=200, null=True)),
                (
                    "site",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="address.municipality",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created By",
                    ),
                ),
            ],
            options={
                "verbose_name": "water",
                "ordering": ["-date_of_collection"],
            },
        ),
        migrations.CreateModel(
            name="Vegetable",
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
                ("date_of_collection", models.DateField(default=datetime.date.today)),
                ("sample_id", models.CharField(max_length=500, unique=True)),
                ("site_image", models.ImageField(upload_to="site_images")),
                ("locality", models.CharField(max_length=500, null=True)),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("CU", "Cucumber"),
                            ("CA", "Cabbage"),
                            ("TO", "Tomato"),
                            ("RA", "Radish"),
                            ("CR", "Carrot"),
                        ],
                        max_length=2,
                    ),
                ),
                ("origin", models.CharField(max_length=200, null=True)),
                (
                    "site",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="address.municipality",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created By",
                    ),
                ),
            ],
            options={
                "verbose_name": "vegetable",
                "ordering": ["-date_of_collection"],
            },
        ),
        migrations.CreateModel(
            name="Stool",
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
                ("date_of_collection", models.DateField(default=datetime.date.today)),
                ("sample_id", models.CharField(max_length=500, unique=True)),
                ("site_image", models.ImageField(upload_to="site_images")),
                ("locality", models.CharField(max_length=500, null=True)),
                (
                    "gender",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female"), ("O", "Others")],
                        max_length=1,
                    ),
                ),
                (
                    "age",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(200),
                        ]
                    ),
                ),
                ("symptoms", models.CharField(max_length=1000, null=True)),
                ("stool_texture", models.CharField(max_length=200, null=True)),
                (
                    "site",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="address.municipality",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created By",
                    ),
                ),
            ],
            options={
                "verbose_name": "stool",
                "ordering": ["-date_of_collection"],
            },
        ),
        migrations.CreateModel(
            name="Standard",
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
                ("date_of_collection", models.DateField(default=datetime.date.today)),
                ("sample_id", models.CharField(max_length=500, unique=True)),
                ("matrix", models.CharField(max_length=200)),
                (
                    "dilution_factor",
                    models.DecimalField(decimal_places=8, max_digits=10),
                ),
                (
                    "expected_concentration",
                    models.DecimalField(decimal_places=8, max_digits=10),
                ),
                (
                    "observed_concentration",
                    models.DecimalField(decimal_places=8, max_digits=10),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created By",
                    ),
                ),
            ],
            options={
                "verbose_name": "standard",
                "ordering": ["-date_of_collection"],
            },
        ),
        migrations.CreateModel(
            name="SlideImage",
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
                (
                    "image",
                    models.ImageField(
                        upload_to="sample_images", verbose_name="Slide Image"
                    ),
                ),
                ("image_id", models.CharField(max_length=100, unique=True)),
                (
                    "image_number",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(15),
                        ]
                    ),
                ),
                (
                    "image_type",
                    models.CharField(
                        choices=[("S", "Smartphone"), ("B", "Brightfield")],
                        default="S",
                        max_length=1,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now=True)),
                (
                    "slide",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="slide_image",
                        to="sample.slide",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="uploaded by",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="slide",
            name="standard_sample",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="standard_slides",
                to="sample.standard",
            ),
        ),
        migrations.AddField(
            model_name="slide",
            name="stool_sample",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="stool_slides",
                to="sample.stool",
            ),
        ),
        migrations.AddField(
            model_name="slide",
            name="vegetable_sample",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="vegetable_slides",
                to="sample.vegetable",
            ),
        ),
        migrations.AddField(
            model_name="slide",
            name="water_sample",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="water_slides",
                to="sample.water",
            ),
        ),
        migrations.AddConstraint(
            model_name="slide",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("water_sample__isnull", False),
                        ("stool_sample__isnull", True),
                        ("vegetable_sample__isnull", True),
                        ("standard_sample__isnull", True),
                    ),
                    models.Q(
                        ("water_sample__isnull", True),
                        ("stool_sample__isnull", False),
                        ("vegetable_sample__isnull", True),
                        ("standard_sample__isnull", True),
                    ),
                    models.Q(
                        ("water_sample__isnull", True),
                        ("stool_sample__isnull", True),
                        ("vegetable_sample__isnull", False),
                        ("standard_sample__isnull", True),
                    ),
                    models.Q(
                        ("water_sample__isnull", True),
                        ("stool_sample__isnull", True),
                        ("vegetable_sample__isnull", True),
                        ("standard_sample__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="only_one_sample",
            ),
        ),
    ]
