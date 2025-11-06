from datetime import date

from django.db.models import Count, Q

from .models import Task


class TaskService:
    @staticmethod
    def get_user_task_statistics(user):
        """Calculate task statistics for a user"""
        tasks = Task.objects.filter(user=user)

        # Use aggregation for better performance (single query instead of multiple)
        stats = tasks.aggregate(
            total_tasks=Count("id"),
            todo_count=Count("id", filter=Q(status="TODO")),
            in_progress_count=Count("id", filter=Q(status="IN_PROGRESS")),
            done_count=Count("id", filter=Q(status="DONE")),
            high_priority_count=Count("id", filter=Q(priority="HIGH")),
            overdue_count=Count(
                "id",
                filter=Q(
                    due_date__lt=date.today(),
                    status__in=["TODO", "IN_PROGRESS"],
                    due_date__isnull=False,
                ),
            ),
        )

        return stats

    @staticmethod
    def get_overdue_tasks(user):
        """Get all overdue tasks for a user"""
        return Task.objects.filter(
            user=user,
            due_date__lt=date.today(),
            status__in=["TODO", "IN_PROGRESS"],
            due_date__isnull=False,
        )

    @staticmethod
    def bulk_update_status(user, task_ids, new_status):
        """Bulk update status for multiple tasks"""
        tasks = Task.objects.filter(user=user, id__in=task_ids)
        tasks.update(status=new_status)
        return tasks.count()
