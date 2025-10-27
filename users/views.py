from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer
from .models import CustomUser


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    Allows any user (even unauthenticated) to send a POST request to register.
    """
    serializer_class = UserRegistrationSerializer

    queryset = CustomUser.objects.all()


    permission_classes = [AllowAny]



    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"message": f"User {user.email} created successfully. Please log in"}, status=status.HTTP_201_CREATED
        )
    