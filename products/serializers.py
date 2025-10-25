from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    owner_username = serializers.ReadOnlyField(source='owner.username')  # ✅ visible in GET
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price',
            'category', 'category_id',
            'stock_quantity', 'image',
            'created_at', 'owner_username'  # ✅ added here
        ]
        read_only_fields = ['id', 'created_at', 'owner_username']

    def validate(self, data):
        if data['price'] <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        if data['stock_quantity'] < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return data

    def create(self, validated_data):
        """
        Automatically assign the logged-in user as the product owner.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)
