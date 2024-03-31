from django.urls import path
from . import views

urlpatterns = [
    path('index/get-weights', views.get_weights, name='get_weights'),
]