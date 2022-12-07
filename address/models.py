from django.db import models

# Create your models here.


class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True, default=None)

    class Meta:
        verbose_name_plural = "provinces"

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name="provinces"
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("name", "province"), name="district_unique_name_province"
            ),
        )

    def __str__(self):
        # return f"{self.name}, {self.province}"
        return self.name


class Municipality(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(
        District, on_delete=models.PROTECT, related_name="districts"
    )

    class Meta:
        verbose_name_plural = "municipalities"

        constraints = (
            models.UniqueConstraint(
                fields=("name", "district"), name="municipality_unique_name_district"
            ),
        )

    def __str__(self):
        # return f"{self.name}, {self.district} ({self.type})"
        return f"{self.name}"


class Ward(models.Model):
    number = models.PositiveSmallIntegerField()
    municipality = models.ForeignKey(
        Municipality, on_delete=models.PROTECT, related_name="municipalities"
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("number", "municipality"),
                name="ward_unique_number_municiplaity",
            ),
        )

    def __str__(self):
        # mun_name = str(self.municipality)
        # return mun_name + "-" + str(self.number)
        return str(self.number)
