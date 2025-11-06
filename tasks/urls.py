from django.urls import path

from .views import (CategoryDetailView, CategoryListCreateView, OverdueTasksView,
                    TaskDetailView, TaskListCreateView, TaskStatisticsView)

urlpatterns = [
    path("tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/statistics/", TaskStatisticsView.as_view(), name="task-statistics"),
    path("tasks/overdue/", OverdueTasksView.as_view(), name="overdue-tasks"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
]
