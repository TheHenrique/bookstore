from django.test import TestCase

from product.factories import CategoryFactory
from product.models import Category
from product.serializers import CategorySerializer


class TestCategorySerializer(TestCase):
    def setUp(self):
        self.category = CategoryFactory(title="tecnologia", slug="tecnologia")

    def test_serializer_accepts_valid_data(self):
        data = {
            "title": "livros",
            "slug": "livros",
            "description": "Categoria de livros",
            "active": True,
        }
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_rejects_duplicate_slug(self):
        data = {"title": "outra categoria", "slug": self.category.slug}
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("slug", serializer.errors)

    def test_serializer_returns_expected_fields(self):
        serializer = CategorySerializer(self.category)
        expected_fields = {"title", "slug", "description", "active"}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_serializer_represents_data_correctly(self):
        serializer = CategorySerializer(self.category)
        self.assertEqual(serializer.data["title"], "tecnologia")
        self.assertEqual(serializer.data["slug"], "tecnologia")

    def test_serializer_creates_category(self):
        data = {"title": "esportes", "slug": "esportes"}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()
        self.assertEqual(Category.objects.filter(slug="esportes").count(), 1)
        self.assertEqual(category.title, "esportes")