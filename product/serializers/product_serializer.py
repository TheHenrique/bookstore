from rest_framework import serializers

from product.models.product import Product, Category
from product.serializers.category_serializer import CategorySerializer


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    categories_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, many=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "active",
            "category",
            "categories_ids",
        ]
        extra_kwargs = {
            "description": {"required": False},
            "category": {"required": False},
            "categories_ids": {"required": False},
        }

    def create(self, validated_data):
        category_data = validated_data.pop("categories_ids")
        product = Product.objects.create(**validated_data)
        for category in category_data:
            product.category.add(category)

        return product
