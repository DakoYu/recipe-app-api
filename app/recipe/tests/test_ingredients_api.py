from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingrdient-list')

class PublicIngredientsAPITests(TestCase):
    '''Test the publicly abailable ingrdients API'''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''Test that login is required to access the endpoint'''
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsAPITests(TestCase):
    '''Test ingredients can be retrieved by authorized user'''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@qq.com',
            'test1234'
        )
        self.client.force_authenticate(self.user)

    def test_retreieve_ingredient(self):
        '''Test retrieivng a list of ingredients'''
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')

        seriliazer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, seriliazer.data)

    def test_ingredients_limited_to_user(self):
        '''test that only ingriedents for the auth user are returned'''
        user2 = get_user_model().objects.create_user(
            'bro@qq.com',
            'test1234'
        )
        Ingredient.objects.create(user=user2, name='kekw')

        ingedient = Ingredient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingedient.name)