from django.conf import settings
from django.db import models


class Task(models.Model):
    STATUS_CHOICES = [
        ("TODO", "To Do"),
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Done"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="Title",
        help_text="Title of the task",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Detailed description of the task",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="TODO",
        verbose_name="Status",
        db_index=True,
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="MEDIUM",
        verbose_name="Priority",
        db_index=True,
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Due Date",
        help_text="Date when the task is due",
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="User",
        db_index=True,
    )
    category = models.ForeignKey(
        "tasks.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        verbose_name="Category",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "priority"]),
            models.Index(fields=["user", "due_date"]),
        ]

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Category Name",
        help_text="Name of the category",
    )
    color = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Color",
        help_text="Color code for the category (e.g., #FF5733)",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="User",
    )

    class Meta:
        unique_together = ("name", "user")
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate category data"""
        from django.core.exceptions import ValidationError

        if self.name:
            self.name = self.name.strip()
            if len(self.name) < 1:
                raise ValidationError({"name": "Category name cannot be empty."})
