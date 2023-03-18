from django.test import TestCase
from account_management.models import User
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status


class UserModelTest(TestCase):

    def setUp(self):
        self.user_name = 'test'
        self.user_email_id = 'test@test.com'
        self.password = '123456'
        self.user = User(username=self.user_name,
                         email=self.user_email_id,
                         password=self.password)
        self.user.save()
        print('user object created')

    def test_model_user(self):
        test = User.objects.get(email='test@test.com')
        self.assertEqual(self.user, test)


class RegisterUserProfileApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.response = self.client.post(reverse('account_management:'
                                                 'registration_url'),
                                         {'username': 'test_user',
                                          'is_superuser': 'True',
                                          'is_staff': 'True',
                                          'is_active': 'True',
                                          'email': 'mail@test.com',
                                          'password': '123456'},
                                         format='json')

    def test_user_creation(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
