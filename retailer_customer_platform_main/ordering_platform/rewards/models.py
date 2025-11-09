from django.db import models
from django.conf import settings

class Reward(models.Model):
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reward_balance')
    points = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.username} - {self.points} coins"

class RewardTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('earn', 'Earn'),
        ('redeem', 'Redeem'),
        ('referral', 'Referral'),
        ('signup_bonus', 'Signup Bonus'),
    ]
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='transactions')
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reward.customer.username} - {self.transaction_type} {self.points}"