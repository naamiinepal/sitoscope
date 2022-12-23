from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sample.models import Slide, SlideImage, Standard, Stool, Vegetable, Water
from sample.serializers import (
    SlideImageSerializer,
    SlideSerializer,
    StandardSerializer,
    StoolSerializer,
    VegetableSerializer,
    WaterSerializer,
)


# Create your views here.
class StandardViewSetAPI(viewsets.ModelViewSet):
    """
    List all standard samples, create new, or retrieve,
    update or delete individual samples.
    """

    queryset = Standard.objects.all()
    serializer_class = StandardSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        slides = Slide.objects.filter(standard_sample=instance.id)
        slides_serializer = SlideSerializer(slides, many=True)

        data = {**serializer.data, "slides": slides_serializer.data}
        for slide_idx, slide in enumerate(data["slides"]):
            images = SlideImage.objects.filter(slide=slide["id"])
            images_serializer = SlideImageSerializer(images, many=True)
            data["slides"][slide_idx].update({"images": images_serializer.data})
        return Response(data)

    @action(detail=True)
    def slides(self, request, pk=None):
        slides = Slide.objects.filter(standard_sample=pk)
        serializer = SlideSerializer(slides, many=True)
        data = {"slides": serializer.data}
        for slide_idx, slide in enumerate(data["slides"]):
            images = SlideImage.objects.filter(slide=slide["id"])
            images_serializer = SlideImageSerializer(images, many=True)
            data["slides"][slide_idx].update({"images": images_serializer.data})
        return Response(data)


class WaterViewSetAPI(viewsets.ModelViewSet):
    """
    List all Water samples, create new, or retrieve,
    update or delete individual samples.
    """

    queryset = Water.objects.all()
    serializer_class = WaterSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        slides = Slide.objects.filter(water_sample=instance.id)
        slides_serializer = SlideSerializer(slides, many=True)

        data = {**serializer.data, "slides": slides_serializer.data}
        for slide_idx, slide in enumerate(data["slides"]):
            images = SlideImage.objects.filter(slide=slide["id"])
            images_serializer = SlideImageSerializer(images, many=True)
            data["slides"][slide_idx].update({"images": images_serializer.data})
        return Response(data)

    @action(detail=True)
    def slides(self, request, pk=None):
        slides = Slide.objects.filter(water_sample=pk)
        serializer = SlideSerializer(slides, many=True)
        data = {"slides": serializer.data}
        for slide_idx, slide in enumerate(data["slides"]):
            images = SlideImage.objects.filter(slide=slide["id"])
            images_serializer = SlideImageSerializer(images, many=True)
            data["slides"][slide_idx].update({"images": images_serializer.data})
        return Response(data)


class VegetableViewSetAPI(viewsets.ModelViewSet):
    """
    List all Vegetable samples, create new, or retrieve,
    update or delete individual samples.
    """

    queryset = Vegetable.objects.all()
    serializer_class = VegetableSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        slides = Slide.objects.filter(vegetable_sample=instance.id)
        slides_serializer = SlideSerializer(slides, many=True)

        data = {**serializer.data, "slides": slides_serializer.data}
        for slide_idx, slide in enumerate(data["slides"]):
            images = SlideImage.objects.filter(slide=slide["id"])
            images_serializer = SlideImageSerializer(images, many=True)
            data["slides"][slide_idx].update({"images": images_serializer.data})
        return Response(data)

    @action(detail=True)
    def slides(self, request, pk=None):
        slides = Slide.objects.filter(vegetable_sample=pk)
        serializer = SlideSerializer(slides, many=True)
        data = {"slides": serializer.data}
        for slide_idx, slide in enumerate(data["slides"]):
            images = SlideImage.objects.filter(slide=slide["id"])
            images_serializer = SlideImageSerializer(images, many=True)
            data["slides"][slide_idx].update({"images": images_serializer.data})
        return Response(data)


class StoolViewSetAPI(viewsets.ModelViewSet):
    """
    List all Stool samples, create new, or retrieve,
    update or delete individual samples.
    """

    queryset = Stool.objects.all()
    serializer_class = StoolSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        slides = Slide.objects.filter(stool_sample=instance.id)
        slides_serializer = SlideSerializer(slides, many=True)

        data = {**serializer.data, "slides": slides_serializer.data}
        for slide_idx, slide in enumerate(data["slides"]):
            images = SlideImage.objects.filter(slide=slide["id"])
            images_serializer = SlideImageSerializer(images, many=True)
            data["slides"][slide_idx].update({"images": images_serializer.data})
        return Response(data)

    @action(detail=True)
    def slides(self, request, pk=None):
        slides = Slide.objects.filter(stool_sample=pk)
        serializer = SlideSerializer(slides, many=True)
        data = {"slides": serializer.data}
        for slide_idx, slide in enumerate(data["slides"]):
            images = SlideImage.objects.filter(slide=slide["id"])
            images_serializer = SlideImageSerializer(images, many=True)
            data["slides"][slide_idx].update({"images": images_serializer.data})
        return Response(data)


class SlideImageViewSetAPI(viewsets.ModelViewSet):
    """
    List the details of an image.
    """

    queryset = SlideImage.objects.all()
    serializer_class = SlideImageSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def partial_update(self, request, *args, **kwargs):
        # update the approved_by field by using django session
        request.data["approved_by"] = request.user.id
        return super().partial_update(request, *args, **kwargs)
