from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from address.models import District, Municipality, Province, Ward
from address.serializers import (
    DistrictSerializer,
    MunicipalitySerializer,
    ProvinceSerializer,
    WardSerializer,
)

# Create your views here.


class ProvinceViewSet(viewsets.ModelViewSet):
    """
    List all provinces, create new province, or retrieve, update and delete a province.
    """

    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    @action(detail=True)
    def districts(self, request, pk=None):
        districts = District.objects.filter(province=pk)
        serializer = DistrictSerializer(districts, many=True)
        return Response({"districts": serializer.data})


class DistrictViewSet(viewsets.ModelViewSet):
    """
    List all Districts, create new District, or retrieve, update and delete a District.
    """

    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    @action(detail=True)
    def municipalities(self, request, pk=None):
        municipalities = Municipality.objects.filter(district=pk)
        serializer = MunicipalitySerializer(municipalities, many=True)
        return Response({"municipalities": serializer.data})


class MunicipalityViewSet(viewsets.ModelViewSet):
    """
    List all Municipalities, create new Municipality, or retrieve, update and delete a Municipality.
    """

    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    @action(detail=True)
    def wards(self, request, pk=None):
        wards = Ward.objects.filter(municipality=pk)
        serializer = WardSerializer(wards, many=True)
        return Response({"wards": serializer.data})


class WardViewSet(viewsets.ModelViewSet):
    """
    List all Wards, create new Ward, or retrieve, update and delete a Ward.
    """

    queryset = Ward.objects.all()
    serializer_class = WardSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
