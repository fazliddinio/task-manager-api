from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(AdminUserCreationForm):
    """
    A form for creating new users. Includes only the email field.
    """
    class Meta:
        model = CustomUser
        fields = ("email")


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        """
        A form for updating existing users. Includes only the email field.
        """
        model = CustomUser
        fields = ("email")

