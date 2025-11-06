from django.contrib import admin

from .models import Category, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "status", "priority", "category", "created_at"]
    list_filter = ["status", "priority", "created_at", "user", "category"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("title", "description", "user")}),
        (
            "Status & Priority",
            {"fields": ("status", "priority", "due_date")},
        ),
        ("Category", {"fields": ("category",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "color"]
    list_filter = ["user"]
    search_fields = ["name"]
    fieldsets = (
        (None, {"fields": ("name", "user", "color")}),
    )
