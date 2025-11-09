from django.contrib import admin
from .models import Reward, RewardTransaction

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('customer', 'points', 'updated_at')

@admin.register(RewardTransaction)
class RewardTransactionAdmin(admin.ModelAdmin):
    list_display = ('reward', 'points', 'transaction_type', 'order', 'created_at')