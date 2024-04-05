from django.urls import path
from . import views

urlpatterns = [
    # path('index/get-weights-old', views.get_weights_old, name='get_weights_old'),
    path('index/get-weights', views.get_weights, name='get_weights'),

    path('tasks/check-task-status', views.check_task_status, name='check_task_status'),
]