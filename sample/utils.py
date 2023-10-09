import os

import nanoid
from django.conf import settings
from django.utils.text import slugify


def upload_samples(instance, filename):
    """
    Generates filename for the sample images.

    For Standard samples, utilizes:
        Sample_type, Date, Sample ID, Slide Number and Image ID

    For Water, Vegetable and Stool samples, utilizes:
        Sample_Type, Site, Date, Sample ID, Slide Number and Image ID

    """
    splitted = filename.rsplit(".", 1)
    ext = "jpg" if len(splitted) == 1 else splitted[1]

    slide_number = instance.slide.slide_number
    image_number = instance.image_id
    if instance.slide.standard_sample:
        sample_type = "standard"
        date = instance.slide.standard_sample.date_of_collection
        sample_id = instance.slide.standard_sample.sample_id
        filename = (
            f"{sample_type}/{date}/{sample_id}/{slide_number}/{image_number}.{ext}"
        )
    else:
        if instance.slide.water_sample:
            sample_type = "water"
            site = instance.slide.water_sample.site
            date = instance.slide.water_sample.date_of_collection
            sample_id = instance.slide.water_sample.sample_id
        elif instance.slide.stool_sample:
            sample_type = "stool"
            site = instance.slide.stool_sample.site
            date = instance.slide.stool_sample.date_of_collection
            sample_id = instance.slide.stool_sample.sample_id
        else:
            sample_type = "vegetable"
            site = instance.slide.vegetable_sample.site
            date = instance.slide.vegetable_sample.date_of_collection
            sample_id = instance.slide.vegetable_sample.sample_id
        filename = f"{sample_type}/{site}/{date}/{sample_id}/{slide_number}/{image_number}.{ext}"
    fullname = os.path.join(settings.MEDIA_ROOT, filename)
    print(fullname)
    if os.path.exists(fullname):
        os.remove(fullname)
    return filename


def create_sample_id(sample_type, date, municipality=None):
    """
    Generate sample id for sample type.
    Args:
    sample_type: ('water', 'stool', 'vegetable')
    date: Date of sample collection
    municipality: Site of sample collection
    """
    site = f"{municipality.district.province.code}-{slugify(municipality.name)}"
    sample_number = nanoid.generate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", 5)
    sample_type = sample_type[0].upper()
    return f"{sample_type}_{site}_{date.strftime('%Y%m%d')}_{sample_number}"


def create_standard_sample_id(date, standard_type, dilution_factor):
    """
    Generate sample id for standard sample type.
    Args:
    date: Date of sample collection
    standard_type: ('water', 'vegetable', 'stool')
    dilution_factor: Dilution factor of standard sample
    """
    sample_type = "Standard_" + standard_type
    sample_number = nanoid.generate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", 5)
    return f"{sample_type}_{date.strftime('%Y%m%d')}_D{slugify(dilution_factor)}_{sample_number}"
