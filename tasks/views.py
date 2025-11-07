from django.db.models import Case, IntegerField, When
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import TaskFilter
from .models import Category, Task
from .pagination import TaskPagination
from .serializers import CategorySerializer, TaskSerializer
from .services import TaskService


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = TaskFilter
    ordering_fields = ["priority", "due_date", "created_at"]
    search_fields = ["title", "description"]
    pagination_class = TaskPagination
    ordering = ["-created_at"]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def filter_queryset(self, queryset):
        """
        Apply filtering and custom priority ordering.
        """
        # Check if priority ordering is requested
        ordering_param = self.request.query_params.get("ordering", "")
        priority_in_ordering = "priority" in ordering_param

        if priority_in_ordering:
            # Remove priority from ordering_fields temporarily to prevent OrderingFilter from handling it
            original_ordering_fields = self.ordering_fields
            self.ordering_fields = [f for f in self.ordering_fields if f != "priority"]

            # Apply filters (excluding OrderingFilter's priority handling)
            queryset = super().filter_queryset(queryset)

            # Restore ordering_fields
            self.ordering_fields = original_ordering_fields

            # Handle custom priority ordering
            ordering_fields = [field.strip() for field in ordering_param.split(",")]

            # Map priority values to integers for proper ordering
            # HIGH=3, MEDIUM=2, LOW=1
            priority_order = Case(
                When(priority="HIGH", then=3),
                When(priority="MEDIUM", then=2),
                When(priority="LOW", then=1),
                default=0,
                output_field=IntegerField(),
            )
            queryset = queryset.annotate(priority_order=priority_order)

            # Build ordering list
            ordering_list = []
            for field in ordering_fields:
                if field == "-priority":
                    ordering_list.append("-priority_order")
                elif field == "priority":
                    ordering_list.append("priority_order")
                else:
                    ordering_list.append(field)

            # Apply default ordering if no other ordering specified
            if not ordering_list:
                ordering_list = self.ordering

            queryset = queryset.order_by(*ordering_list)
        else:
            # Use standard filtering
            queryset = super().filter_queryset(queryset)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    # Note: handle_exception won't catch DoesNotExist because DRF's
    # get_object() raises Http404, not DoesNotExist. The queryset filtering
    # by user already ensures users can only access their own tasks.


class TaskStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = TaskService.get_user_task_statistics(request.user)
        return Response(stats)


class OverdueTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaskService.get_overdue_tasks(self.request.user)


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
