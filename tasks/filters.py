from django_filters import rest_framework as filters

from .models import Task


class TaskFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr="icontains")
    due_date_from = filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_date_to = filters.DateFilter(field_name="due_date", lookup_expr="lte")

    class Meta:
        model = Task
        fields = ["status", "priority", "title", "due_date"]
