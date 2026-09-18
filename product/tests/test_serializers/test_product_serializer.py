from django.test import TestCase

from product.factories import CategoryFactory, ProductFactory
from product.models import Product
from product.serializers import ProductSerializer


class TestProductSerializer(TestCase):
    def setUp(self):
        self.category = CategoryFactory(title="livros")
        self.product = ProductFactory(
            title="Dom Casmurro", price=40, category=[self.category]
        )

    def test_serializer_accepts_valid_data(self):
        data = {
            "title": "Memorias Postumas",
            "price": 35,
            "categories_ids": [self.category.id],
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_title(self):
        data = {"price": 35, "categories_ids": [self.category.id]}
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_serializer_requires_price(self):
        data = {"title": "sem preco", "categories_ids": [self.category.id]}
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_serializer_rejects_title_too_long(self):
        data = {
            "title": "a" * 256,
            "price": 10,
            "categories_ids": [self.category.id],
        }
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_serializer_rejects_nonexistent_category(self):
        data = {"title": "produto invalido", "price": 10, "categories_ids": [999999]}
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("categories_ids", serializer.errors)

    def test_serializer_returns_expected_fields(self):
        serializer = ProductSerializer(self.product)
        expected_fields = {
            "id", "title", "description", "price", "active", "category",
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_serializer_represents_category_relationship(self):
        serializer = ProductSerializer(self.product)
        self.assertEqual(
            serializer.data["category"][0]["title"], self.category.title
        )

    def test_serializer_creates_product_with_category(self):
        data = {
            "title": "novo produto",
            "price": 99,
            "categories_ids": [self.category.id],
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(Product.objects.filter(title="novo produto").count(), 1)
        self.assertEqual(product.category.count(), 1)
        self.assertEqual(product.category.first().title, self.category.title)