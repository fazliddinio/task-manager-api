from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user model.
    """
    def 