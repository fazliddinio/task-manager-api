from datetime import date

from rest_framework import serializers

from .models import Category, Task


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none(), required=False, allow_null=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter category queryset by user if request is available
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["category"].queryset = Category.objects.filter(
                user=request.user
            )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "category",
            "user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters long"
            )
        return value

    def validate_due_date(self, value):
        if value and value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past")
        return value

    def validate(self, data):
        if data.get("status") == "DONE" and data.get("priority") == "HIGH":
            if (
                "due_date" in data
                and data["due_date"]
                and data["due_date"] > date.today()
            ):
                raise serializers.ValidationError(
                    "Cannot mark high priority task as done if due date is in the future"
                )
        return data

    def validate_category(self, value):
        if value is None:
            return value
        request = self.context.get("request")
        if request and value.user != request.user:
            raise serializers.ValidationError("Invalid category for this user")
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "color"]

    def validate_name(self, value):
        """Validate category name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        value = value.strip()
        if len(value) < 1:
            raise serializers.ValidationError(
                "Category name must be at least 1 character long."
            )
        if len(value) > 100:
            raise serializers.ValidationError(
                "Category name cannot exceed 100 characters."
            )
        return value

    def validate(self, data):
        """Validate category uniqueness per user"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            name = data.get("name", "").strip()
            if name:
                # Check for duplicate category name for this user
                existing = Category.objects.filter(
                    user=request.user, name__iexact=name
                )
                # Exclude current instance if updating
                if self.instance:
                    existing = existing.exclude(pk=self.instance.pk)
                if existing.exists():
                    raise serializers.ValidationError(
                        {"name": "You already have a category with this name."}
                    )
        return data
