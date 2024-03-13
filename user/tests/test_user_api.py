from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')



def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the publicly feature of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a user is successful"""
        payload = {'email': 'test@example.com', 'password': 'testpass123', 'name': 'Test Name'}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
    #
    # def test_password_too_short(self):
    #     payload = {'email': 'test@example.com', 'password': 'testpass123', 'name': 'Test Name'}
    #     res = self.client.post(CREATE_USER_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_existing_email(self):
        """Test creating a user with that email already exists"""
        payload = {'email': 'test@example.com', 'password': 'testpass123', 'name': 'Test Name'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertTrue(user_exists)

    def test_create_token_for_user(self):
        """Test creating a token for user"""
        user_details = {'email': 'test@example.com', 'password': 'testpass123', 'name': 'Test Name'}
        create_user(**user_details)
        payload = {'email': user_details['email'], 'password': user_details['password']}
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test creating invalid credentials """
        create_user(email='test@example.com', password='testpass123')

        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test creating a blank password returns an error."""
        payload = {'email': 'test@example.com', 'password': 'testpass123'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


