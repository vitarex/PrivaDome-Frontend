""" API tests. """
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from django.urls import reverse
from django.contrib.auth.models import User


def authenticate_client_admin(client):
    """ Create an admin token for the client. """
    token = Token.objects.get(user__username='adminUser')
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

def authenticate_client_regular(client):
    """ Create a regular token for the client. """
    token = Token.objects.get(user__username='regularUser')
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


class UserTests(APITestCase):
    """ User object tests. """

    def setUp(self):
        """ Set up test bed. """
        user = User.objects.create_user(username='adminUser',
                                        email='adminEmail@test.test',
                                        password='adminPassword')

        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save()

        Token.objects.create(key="adminTokenKey", user_id=1)

        user = User.objects.create_user(username='regularUser',
                                        email='regularEmail@test.test',
                                        password='regularPassword')

        Token.objects.create(key="regularTokenKey", user_id=2)

        user = User.objects.create_user(username='otherUser',
                                        email='otherEmail@test.test',
                                        password='otherPassword')


    def test_get_users(self):
        """
        Ensure we can retrieve the User objects.
        """
        # Reverse url for Users
        # The router makes prefixed uniqe names for the different methods.
        url = reverse('user-list')
        # The Client must be authorized
        authenticate_client_admin(self.client)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(User.objects.count(), 3)

    def test_create_user(self):
        """
        Ensure we can create a new User object.
        """
        url = reverse('user-list')
        data = {
            'username': 'newUser',
            'password': 'newPassword',
            'email': 'newEmail@test.test'
            }

        authenticate_client_admin(self.client)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(User.objects.get(id=4).username, 'newUser')

    def test_delete_user(self):
        """
        Ensure we can delete Users
        """
        url = reverse('user-detail', args=[1])

        authenticate_client_admin(self.client)
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 2)

    def test_update_user(self):
        """
        Ensure can update Users.
        """
        url = reverse('user-detail', args=[1])

        data = {
            'username': 'modifiedUser',
            'newPassword': 'modifiedPassword',
            'email': 'modifiedEmail@test.test',
            'oldPassword': 'adminPassword'
            }

        authenticate_client_admin(self.client)
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(id=1).username, 'modifiedUser')
        self.assertEqual(User.objects.get(id=1).email,
                         'modifiedEmail@test.test')
        self.assertEqual(User.objects.get(id=1)
                         .check_password('modifiedPassword'), True)

    def test_update_user_partial(self):
        """
        Ensure can update Users.
        """
        url = reverse('user-detail', args=[1])

        data = {
            'username': 'modifiedUser',
            'oldPassword': 'adminPassword'
            }

        authenticate_client_admin(self.client)
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(id=1).username, 'modifiedUser')
        self.assertEqual(User.objects.get(id=1).email,
                         'adminEmail@test.test')
        self.assertEqual(User.objects.get(id=1)
                         .check_password('adminPassword'), True)

    def test_update_user_incorrect_password(self):
        """
        Ensure can update Users.
        """
        url = reverse('user-detail', args=[1])

        data = {
            'username': 'modifiedUser',
            'oldPassword': 'incorrectPassword'
            }

        authenticate_client_admin(self.client)
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Incorrect password")
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(id=1).username, 'adminUser')
        self.assertEqual(User.objects.get(id=1).email,
                         'adminEmail@test.test')
        self.assertEqual(User.objects.get(id=1)
                         .check_password('adminPassword'), True)

    def test_update_user_no_password(self):
        """
        Ensure can update Users.
        """
        url = reverse('user-detail', args=[1])

        data = {
            'username': 'modifiedUser'
            }

        authenticate_client_admin(self.client)
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Password not provided")
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(id=1).username, 'adminUser')
        self.assertEqual(User.objects.get(id=1).email,
                         'adminEmail@test.test')
        self.assertEqual(User.objects.get(id=1)
                         .check_password('adminPassword'), True)

    def test_create_user_regular(self):
        """
        Ensure regular users cannot create a new User object.
        """
        url = reverse('user-list')
        data = {
            'username': 'newUser',
            'password': 'newPassword',
            'email': 'newEmail@test.test'
            }

        authenticate_client_regular(self.client)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 3)

    def test_delete_user_regular_another(self):
        """
        Ensure regular users cannot delete another User object.
        """
        url = reverse('user-detail', args=[3])

        authenticate_client_regular(self.client)
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 3)

    def test_delete_user_regular_self(self):
        """
        Ensure regular users can delete themselves.
        """
        url = reverse('user-detail', args=[2])

        authenticate_client_regular(self.client)
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 2)

    def test_update_user_regular_another(self):
        """
        Ensure regular users cannot update another User object.
        Even with the correct password.
        """
        url = reverse('user-detail', args=[3])

        data = {
            'username': 'modifiedUser',
            'newPassword': 'modifiedPassword',
            'email': 'modifiedEmail@test.test',
            'oldPassword': 'otherPassword'
            }

        authenticate_client_regular(self.client)
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(id=3).username, 'otherUser')
        self.assertEqual(User.objects.get(id=3).email,
                         'otherEmail@test.test')
        self.assertEqual(User.objects.get(id=3)
                         .check_password('otherPassword'), True)

    def test_update_user_regular_self(self):
        """
        Ensure regular users can update themselves.
        """
        url = reverse('user-detail', args=[2])

        data = {
            'username': 'modifiedUser',
            'newPassword': 'modifiedPassword',
            'email': 'modifiedEmail@test.test',
            'oldPassword': 'regularPassword'
            }

        authenticate_client_regular(self.client)
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(id=2).username, 'modifiedUser')
        self.assertEqual(User.objects.get(id=2).email,
                         'modifiedEmail@test.test')
        self.assertEqual(User.objects.get(id=2)
                         .check_password('modifiedPassword'), True)

    def test_get_users_regular(self):
        """
        Ensure regular users can can only see themselves.
        """
        url = reverse('user-list')

        authenticate_client_regular(self.client)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], {'id': 2, 'username': 'regularUser',\
                                           'email': 'regularEmail@test.test',\
                                           'admin': False})
        self.assertEqual(User.objects.count(), 3)


class LoginTest(APITestCase):
    """ Login endpoint tests. """

    def setUp(self):
        """ Set up test bed. """
        User.objects.create_user(username='adminUser',
                                 email='adminEmail@test.test',
                                 password='adminPassword')
        Token.objects.create(key="adminTokenKey", user_id=1)

    def test_login_correct(self):
        """
        Ensure users can log in with correct credentials.
        """
        url = reverse('login')
        data = {
            'username': 'adminUser',
            'password': 'adminPassword'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['token'], 'adminTokenKey')

    def test_login_incorrect_password(self):
        """
        Ensure users can't log in with incorrect password.
        """
        url = reverse('login')
        data = {
            'username': 'adminUser',
            'password': 'adminPassworda'
        }

        response = self.client.post(url, data, format='json')

        self.assertNotContains(response, 'token', 400)

    def test_login_incorrect_username(self):
        """
        Ensure users can't log in with non-existent username.
        """
        url = reverse('login')
        data = {
            'username': 'adminUsera',
            'password': 'adminPassword'
        }

        response = self.client.post(url, data, format='json')

        self.assertNotContains(response, 'token', 400)
