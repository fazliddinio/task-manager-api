from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser


class UserAuthenticationTests(APITestCase):
    
    def setUp(self):
        """
        Set up common variables for our tests.
        'reverse' is a utility that finds the URL path for a given URL 'name'.
        This is better than hard-coding '/api/register/'
        """

        self.register_url = reverse('user-register')
        self.login_url = reverse('token_obtain_pair')

        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123',
        }

    def test_user_registration_success(self):
        """
        Test that a new user can be registered successfully.
        """

        response = self.client.post(self.register_url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], f"User {self.user_data['email']} created successfully. Please log in")
        self.assertTrue(CustomUser.objects.filter(email=self.user_data['email']).exists())

    
    def test_user_registration_password_mismatch(self):
        """
        Test that registration fails if passwords do not match.
        """

        data = self.user_data.copy()
        data['password2'] = 'mismatchingpassword'

        response = self.client.post(self.register_url, data, format = 'json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(CustomUser.objects.filter(email=self.user_data['email']).exists())
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'][0], 'Password fields did not match')


    def test_user_login_success(self):
        """
        Test that a registered user can log in and recieve tokens.
        """

        CustomUser.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
            }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


    def test_user_login_invalid_credentials(self):
        """
        Test that login fails with incorrect password.
        """

        login_data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword',
        }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)