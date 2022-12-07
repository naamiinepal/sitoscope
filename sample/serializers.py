from rest_framework import serializers
from sample.models import Standard, Water, Stool, Vegetable, Slide, SlideImage
from sample.const import IMAGE_TYPE_CHOICES


# Create serializers here


def create_standard_sample_id(date):
    # Utility to create standard sample id
    sample_number = str(Standard.objects.all().count() + 1).zfill(4)
    return f"Standard_{date.strftime('%Y%m%d')}_{sample_number}"


class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = [
            "user",
            "date_of_collection",
            "matrix",
            "dilution_factor",
            "expected_concentration",
            "observed_concentration",
        ]

    def create(self, validated_data):
        validated_data["sample_id"] = create_standard_sample_id(
            validated_data["date_of_collection"]
        )
        standard_sample = Standard(**validated_data)
        print(f"Saving sample {standard_sample}")
        standard_sample.save()
        for i in range(3):
            # TODO: Don't use number here directly, get number from config
            slide = Slide(standard_sample=standard_sample, slide_number=i + 1)
            print(f"Saving slide {slide}")
            slide.save()
            for j in range(15):  # TODO: get number from config
                for image_type, _ in IMAGE_TYPE_CHOICES:
                    slide_image = SlideImage(
                        uploaded_by=validated_data.get("user"),
                        slide=slide,
                        image="",
                        image_type=image_type,
                        image_id=f"{standard_sample}_S{i+1}_I{j+1}_{image_type}",
                        image_number=j + 1,
                    )
                    print(f"Saving image {slide_image}")
                    slide_image.save()
        print(f"Finished creating sample {standard_sample}")
        return standard_sample


class WaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water
        fields = "__all__"


class StoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stool
        fields = "__all__"


class VegetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vegetable
        fields = "__all__"


class SlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slide
        fields = "__all__"


class SlideImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlideImage
        fields = "__all__"
