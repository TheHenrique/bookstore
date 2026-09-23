from django.test import TestCase

from order.factories import OrderFactory, UserFactory
from order.serializers import OrderSerializer
from product.factories import CategoryFactory, ProductFactory


class TestOrderSerializer(TestCase):
    def setUp(self):
        self.category = CategoryFactory(title="livros")
        self.product_1 = ProductFactory(
            title="Dom Casmurro", price=40, category=[self.category]
        )
        self.product_2 = ProductFactory(
            title="Memorias Postumas", price=30, category=[self.category]
        )
        self.order = OrderFactory(product=[self.product_1, self.product_2])

    def test_serializer_accepts_valid_data(self):
        user = UserFactory()
        data = {"user": user.id, "product_ids": [self.product_1.id]}
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_user(self):
        data = {"product_ids": [self.product_1.id]}
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("user", serializer.errors)

    def test_serializer_requires_product_ids(self):
        user = UserFactory()
        data = {"user": user.id}
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("product_ids", serializer.errors)

    def test_serializer_rejects_nonexistent_product(self):
        user = UserFactory()
        data = {"user": user.id, "product_ids": [999999]}
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("product_ids", serializer.errors)

    def test_serializer_returns_expected_fields(self):
        serializer = OrderSerializer(self.order)
        expected_fields = {"product", "total", "user"}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_serializer_represents_products_relationship(self):
        serializer = OrderSerializer(self.order)
        titles = {p["title"] for p in serializer.data["product"]}
        self.assertEqual(titles, {self.product_1.title, self.product_2.title})

    def test_serializer_calculates_total(self):
        serializer = OrderSerializer(self.order)
        expected_total = self.product_1.price + self.product_2.price
        self.assertEqual(serializer.data["total"], expected_total)

    def test_serializer_creates_order(self):
        user = UserFactory()
        data = {
            "user": user.id,
            "product_ids": [self.product_1.id, self.product_2.id],
        }
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        self.assertEqual(order.product.count(), 2)