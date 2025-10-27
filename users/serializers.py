from rest_framework import serializers
from .models import CustomUser
from django.core.exceptions import ValidationError


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for the user model.
    """

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = CustomUser
        fields = ['email', 
                  'password', 
                  'password2', 
                  'first_name', 
                  'last_name',
                  ]


        extra_kwargs = {
            'password': 
            {'write_only': True, 'style': 
             {'input_type': 'password'}}
        }


    def validate(self, attrs):
        """
        Check that the two password entries match.
        """

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Password fields did not match'})
        
        if len(attrs['password']) < 8:
            raise serializers.ValidationError({'password': "Password must be at least 8 characters long. "})
        

        return attrs


    def create(self, validated_data):
        """
        Create and return a new user with a hashed password.
        """
        validated_data.pop('password2')

        password = validated_data.pop('password')

        user = CustomUser.objects.create_user(password=password, **validated_data)

        return user