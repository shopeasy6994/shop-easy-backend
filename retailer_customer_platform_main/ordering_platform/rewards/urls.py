from django.urls import path
from . import views

urlpatterns = [
    path('balance/', views.get_reward_balance, name='get_reward_balance'),
]