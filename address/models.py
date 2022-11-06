from django.db import models

# Create your models here.
class Province(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'province'
        ordering = ['-name']

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.RESTRICT)

    class Meta:
        db_table = 'district'
        constraints = (
            models.UniqueConstraint(
                fields=["name", "province"], name="district_unique_name_province"
            ),
        )

    def __str__(self):
        return self.name


class Site(models.Model):
    name = models.CharField(max_length=500)
    district = models.ForeignKey(District, on_delete=models.RESTRICT)

    class Meta:
        db_table = 'site'
        constraints = (
            models.UniqueConstraint(
                fields=["name", "district"], name="site_unique_name_district"
            ),
        )

    def __str__(self):
        return self.name