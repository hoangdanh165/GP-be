from ..models.service import Service
from rest_framework import serializers
from .category import CategorySerializer
from ..models.category import Category


class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "category",
            "description",
            "price",
            "discount",
            "discount_from",
            "discount_to",
            "estimated_duration",
            "create_at",
        ]


class ServiceUpdateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False
    )
    new_category = serializers.CharField(write_only=True, required=False)
    new_category_description = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Service
        fields = [
            "name",
            "category",
            "new_category",
            "new_category_description",
            "description",
            "price",
            "discount",
            "discount_from",
            "discount_to",
            "estimated_duration",
        ]

    def validate(self, attrs):
        new_category_name = attrs.get("new_category")
        new_category_description = attrs.get("new_category_description")

        if new_category_name:
            category, created = Category.objects.get_or_create(
                name=new_category_name,
                defaults={"description": new_category_description},
            )

            if not created and new_category_description:
                category.description = new_category_description
                category.save()

            attrs["category"] = category

        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("new_category", None)
        validated_data.pop("new_category_description", None)
        return super().update(instance, validated_data)
