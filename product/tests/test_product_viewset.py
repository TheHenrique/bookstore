import json

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from django.urls import reverse

from product.factories import ProductFactory, CategoryFactory
from order.factories import UserFactory
from product.models import Product


class TestProductViewSet(APITestCase):

    client = APIClient()

    def setUp(self):
        self.user = UserFactory()
        token = Token.objects.create(user=self.user)
        token.save()
        self.product = ProductFactory(
            title="Mouse",
            price=50.00,
        )

    def test_get_all_products(self):
        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse("product-list", kwargs={"version": "v1"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product_data = json.loads(response.content)
        self.assertEqual(product_data["results"][0]["title"], self.product.title)
        self.assertEqual(
            float(product_data["results"][0]["price"]), float(self.product.price)
        )
        self.assertEqual(product_data["results"][0]["active"], self.product.active)

    def test_create_product(self):
        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        category = CategoryFactory()
        data = json.dumps(
            {
                "title": "Keyboard",
                "price": 80.00,
                "categories_ids": [category.id],
                "slug": "keyboard",
                "description": "A very good mechanical keyboard",
                "active": True,
            }
        )
        response = self.client.post(
            reverse("product-list", kwargs={"version": "v1"}),
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_product = Product.objects.get(title="Keyboard")
        self.assertEqual(created_product.price, 80.00)
        self.assertEqual(created_product.title, "Keyboard")
