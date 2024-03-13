import datetime
from collections.abc import Iterable

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.views.generic import TemplateView
from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from address.models import Province
from sample.const import DEFAULT_FILTER_RANGE_START, STANDARD_SAMPLE_TYPES
from sample.models import Stool, Vegetable, Water


def get_model_queryset(sample_type, start_date, end_date, province):
    if sample_type == "Water":
        return Water.objects.filter(
            date_of_collection__range=[start_date, end_date],
            site__district__province__code=province,
        )
    if sample_type == "Vegetable":
        return Vegetable.objects.filter(
            date_of_collection__range=[start_date, end_date],
            site__district__province__code=province,
        )
    if sample_type == "Stool":
        return Stool.objects.filter(
            date_of_collection__range=[start_date, end_date],
            site__district__province__code=province,
        )
    raise NotImplementedError(f"{sample_type} does not exist.")


class FilterSamples(APIView):
    """
    View to list all samples' count in the system.

    * Only admin users are able to access this view.
    """

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, format=None):
        filter_range: str = request.GET.get("filter_date_range", "")
        provinces: str = request.GET.getlist("province", "")
        sample_types: str = request.GET.getlist("sample", "")

        if filter_range:
            start_date, end_date = filter_range.split(" - ")
        else:
            start_date = request.GET.get("from", DEFAULT_FILTER_RANGE_START)
            today_date = datetime.datetime.today().strftime("%Y-%m-%d")
            end_date = request.GET.get("to", today_date)

        user_provinces = request.user.profile.provinces.all()
        if provinces:
            if not isinstance(provinces, Iterable):
                # If not a list, convert to list
                provinces = [provinces]
            for p in provinces:
                if not user_provinces.filter(code=p):
                    raise PermissionDenied(
                        f"No permission to view items from Province {p}"
                    )
        else:
            provinces = [province.code for province in user_provinces]

        if sample_types:
            if not isinstance(sample_types, Iterable):
                sample_types = [sample_types]
            for sample in sample_types:
                if sample not in [name for _, name in STANDARD_SAMPLE_TYPES]:
                    raise NotImplementedError(f"{sample} does not exist.")
        else:
            sample_types = [name for _, name in STANDARD_SAMPLE_TYPES]

        data = {"start_date": start_date, "end_date": end_date, "data": {}}
        for sample_type_name in sample_types:
            data["data"].update({sample_type_name: {}})
            for province in provinces:
                province_name = Province.objects.get(code=province).name
                queryset = get_model_queryset(
                    sample_type_name,
                    start_date=start_date,
                    end_date=end_date,
                    province=province,
                )
                data["data"][sample_type_name].update(
                    {
                        province_name: {
                            "by_month": queryset.annotate(
                                month=TruncMonth("date_of_collection")
                            )  # Truncate to month and add to select list
                            .values("month")  # Group By month
                            .annotate(
                                count=Count("id")
                            )  # Select the count of the grouping
                            .values("month", "count"),
                            "total_count": queryset.count(),
                        }
                    }
                )
        return Response(data)
