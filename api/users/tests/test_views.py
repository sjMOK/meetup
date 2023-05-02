import json

from django.contrib.sessions.backends.db import SessionStore

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from ..models import User, UserType
from ..serializers import UserSerializer


class LoginViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user_type = UserType.objects.create(name='admin', possible_duration=0)
        cls.user = User.objects.create_user(username='username', name='name', email='email@naver.com', password='password', user_type=user_type)

    def test_success(self):
        response = self.client.post('/users/login', {'username': 'username', 'password': 'password'}, format='json')
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(body_data, str(self.user))
        self.assertIn('sessionid', response.cookies)
        self.assertIn('csrftoken', response.cookies)

    def test_fail_with_wrong_credentials(self):
        response = self.client.post('/users/login', {'username': 'username', 'password': 'wrong_password'}, format='json')
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(body_data, {'detail': 'No matching user.'})

    def test_validation_fail(self):
        response = self.client.post('/users/login', {'username': 'username'}, format='json')
        self.assertContains(response, 'password', status_code=HTTP_400_BAD_REQUEST)


class LogoutViewTestCase(APITestCase):
    def test(self):
        user_type = UserType.objects.create(name='admin', possible_duration=0)
        User.objects.create_user(username='username', name='name', email='email@naver.com', password='password', user_type=user_type)
        s = SessionStore()
        
        login_response = self.client.post('/users/login', {'username': 'username', 'password': 'password'}, format='json')
        session_id = login_response.cookies['sessionid'].value
        self.assertTrue(s.exists(session_id))
        
        self.client.post('/users/logout')
        self.assertFalse(s.exists(session_id))


class UserViewSetTestCase(APITestCase):
    url = '/users'

    @classmethod
    def setUpTestData(cls):
        admin_user_type = UserType.objects.create(id=1, name='admin', possible_duration=0)
        cls.user_type = UserType.objects.create(name='undergraduate', possible_duration=1)

        cls.admin_user = User.objects.create_user(username='admin', name='admin', email='admin@naver.com', password='password', user_type=admin_user_type)
        cls.user = User.objects.create_user(username='user', name='user', email='user@naver.com', password='password', user_type=cls.user_type)

    def test_get_by_admin_user(self):
        self.url += f'/{self.user.id}'

        self.client.force_authenticate(self.admin_user)
        response = self.client.get(self.url)
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertDictEqual(body_data, UserSerializer(self.user).data)

    def test_get_by_normal_user(self):
        self.url += f'/{self.user.id + 1}'

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertDictEqual(body_data, UserSerializer(self.user).data)

    def test_get_by_anonymous_user(self):
        self.url += f'/{self.user.id}'

        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_list_by_admin_user(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(self.url)
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertListEqual(body_data, UserSerializer(User.objects.all(), many=True).data)

    def test_list_by_normal_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_list_by_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_create(self):
        request_data = {
            'username': 'newusername',
            'password': 'password',
            'name': 'newname',
            'email': 'new@naver.com',
            'user_type': self.user_type.id,
        }
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.url, request_data, format='json')
        created_user_id = response.get('Location')

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(id=created_user_id).exists())

    def test_create_by_normal_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
    
    def test_create_by_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_partial_update_by_admin_user(self):
        self.url += f'/{self.user.id}'
        reqeust_data = {'name': 'newname', 'email': 'new@naver.com'}

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.url, reqeust_data, format='json')
        user = User.objects.get(id=self.user.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(user.name, reqeust_data['name'])
        self.assertEqual(user.email, reqeust_data['email'])

    def test_partial_update_by_normal_user(self):
        self.url += f'/{self.user.id + 1}'
        reqeust_data = {'name': 'newname', 'email': 'new@naver.com'}

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, reqeust_data, format='json')
        user = User.objects.get(id=self.user.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(user.name, reqeust_data['name'])
        self.assertEqual(user.email, reqeust_data['email'])

    def test_normal_user_try_to_update_non_patchable_field(self):
        self.url += f'/{self.user.id}'
        reqeust_data = {'username': 'newusername', 'name': 'newname', 'email': 'new@naver.com'}

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, reqeust_data, format='json')
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(body_data, 'The data contains fields cannot be updated.')

    def test_admin_user_try_to_update_non_patchable_field(self):
        self.url += f'/{self.user.id}'
        reqeust_data = {'username': 'newusername', 'name': 'newname', 'email': 'new@naver.com'}

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.url, reqeust_data, format='json')

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_partial_update_by_anonymous_user(self):
        self.url += f'/{self.user.id}'
        reqeust_data = {'name': 'newname', 'email': 'new@naver.com'}

        self.client.force_authenticate(user=None)
        response = self.client.patch(self.url, reqeust_data, format='json')

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_delete_by_admin_user(self):
        self.url += f'/{self.user.id}'

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_by_normal_user(self):
        self.url += f'/{self.user.id + 1}'

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_by_anonymous_user(self):
        self.url += f'/{self.user.id}'

        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
