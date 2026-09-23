import json

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from django.urls import reverse

from product.factories import ProductFactory, CategoryFactory
from order.factories import OrderFactory, UserFactory
from order.models import Order
from product.models import Product


class TestOrderViewSet(APITestCase):

    client = APIClient()

    def setUp(self):
        self.user = UserFactory()
        token = Token.objects.create(user=self.user)
        token.save()

        self.category = CategoryFactory(title="Technology")
        self.product = ProductFactory(
            category=[self.category], title="Laptop", price=999.99
        )
        self.order = OrderFactory(product=(self.product,))

    def test_order(self):
        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse("order-list", kwargs={"version": "v1"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_data = json.loads(response.content)
        self.assertEqual(
            order_data["results"][0]["product"][0]["title"], self.product.title
        )
        self.assertEqual(
            float(order_data["results"][0]["product"][0]["price"]),
            float(self.product.price),
        )
        self.assertEqual(
            order_data["results"][0]["product"][0]["active"], self.product.active
        )
        self.assertEqual(
            order_data["results"][0]["product"][0]["category"][0]["title"],
            self.category.title,
        )

    def test_create_order(self):
        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        user = UserFactory()
        product = ProductFactory()
        data = json.dumps({"product_ids": [product.id], "user": user.id})
        response = self.client.post(
            reverse("order-list", kwargs={"version": "v1"}),
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_order = Order.objects.get(user=user)

    def test_get_single_order(self):
        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse(
            "order-detail",
            kwargs={"version": "v1", "pk": self.order.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_data = json.loads(response.content)
        self.assertEqual(order_data["product"][0]["title"], self.product.title)

    def test_delete_order(self):
        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse(
            "order-detail",
            kwargs={"version": "v1", "pk": self.order.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_order_requires_authentication(self):
        url = reverse("order-list", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)