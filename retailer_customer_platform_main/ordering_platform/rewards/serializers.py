from rest_framework import serializers
from .models import Reward, RewardTransaction

class RewardTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardTransaction
        fields = ['points', 'transaction_type', 'created_at']

class RewardSerializer(serializers.ModelSerializer):
    transactions = RewardTransactionSerializer(many=True, read_only=True)
    class Meta:
        model = Reward
        fields = ['points', 'updated_at', 'transactions']