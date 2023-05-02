from categories.serializers import CategorySerializer
from core.models import Category
from django.test import TestCase
from django.urls import reverse
from helpers.test_helpers import create_category, create_user
from rest_framework import status
from rest_framework.test import APIClient

CATEGORIES_URL = reverse('api:categories-list')


def detail_url(id):
    return reverse('api:categories-detail', args=[id])


class PublicCategoriesApiTests(TestCase):
    """
    Tests for unauthenticated categories api requests
    """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

    def test_list_categories(self):
        """
        Fetching list of categories
        should return 200 - OK and return the list of categories
        """
        for i in range(5):
            create_category(name=f"category{i}")
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True)
        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serialized_categories.data)

    def test_fetch_single_category(self):
        """
        Fetching a single category
        should return 200 - OK and return a single category
        """
        category = create_category()
        url = detail_url(category.id)
        res = self.client.get(url)
        serialized_category = CategorySerializer(category)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_category.data)

    def test_updating_category(self):
        """
        Unauthenticed request to update a category
        should return 401 - Unauthorized
        """
        category = create_category()
        url = detail_url(category.id)
        res = self.client.patch(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deleting_category(self):
        """
        Unauthenticed request to delete a category
        should return 401 - Unauthorized
        """
        category = create_category()
        url = detail_url(category.id)
        res = self.client.patch(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoriesApiTests(TestCase):
    """
    Tests for authenticated categories api requests
    """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.staff = create_user(
            email='staff@email.com',
            password='testpass',
            username='staffusername',
            first_name='first name',
            last_name='last name',
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_list_categories(self):
        """
        Fetching list of categories
        should return 200 - OK and return the list of categories
        """
        for i in range(5):
            create_category(name=f"category{i}")
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True)
        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serialized_categories.data)

    def test_fetch_single_category(self):
        """
        Fetching a single category
        should return 200 - OK and return a single category
        """
        category = create_category()
        serialized_category = CategorySerializer(category)
        url = detail_url(category.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_category.data)

    def test_create_category(self):
        """
        Creating a category
        should return 201 - Created and return the category
        """
        self.client.force_authenticate(self.staff)
        initial_category_count = Category.objects.all().count()
        payload = {
            'name': 'Test Name'
        }
        res = self.client.post(CATEGORIES_URL, payload)
        current_count = Category.objects.all().count()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_count, initial_category_count + 1)
        self.assertEqual(res.data['name'], payload['name'].lower())

    def test_create_category_with_normal_user(self):
        """
        Normal users are not allowed to create a category
        should return 403 - Forbidden
        """
        payload = {
            'name': 'Test Name'
        }
        res = self.client.post(CATEGORIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_update_category(self):
        """
        Patching category
        should return 200 - OK and reflects on the db
        """
        self.client.force_authenticate(self.staff)
        category = create_category(name='initial name')
        payload = {
            'name': 'New Name'
        }
        url = detail_url(category.id)
        res = self.client.patch(url, payload)
        category.refresh_from_db()
        serialized_category = CategorySerializer(category)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_category.data)

    def test_patch_update_with_normal_user(self):
        """
        Normal users are not allowed to update/patch
        should return 403 - Forbidden
        """
        category = create_category(name='initial name')
        payload = {
            'name': 'New Name'
        }
        url = detail_url(category.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category(self):
        """
        Deleting a category
        should retunr 204 - No Content
        """
        self.client.force_authenticate(self.staff)
        category = create_category()
        url = detail_url(category.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_delete_category_with_normal_user(self):
        """
        Normal users are not allowed to delete
        should return 403 - Forbidden
        """
        category = create_category()
        url = detail_url(category.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
