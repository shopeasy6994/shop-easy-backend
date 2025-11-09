from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_item_request, name='submit_item_request'),
]