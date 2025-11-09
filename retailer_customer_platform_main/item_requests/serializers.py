from rest_framework import serializers
from .models import ItemRequest

class ItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemRequest
        fields = ['id', 'item_name', 'quantity', 'expected_price', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']