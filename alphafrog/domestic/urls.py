from django.urls import path
from .views import index_views

urlpatterns = [
    # path('index/get-weights-old', views.get_weights_old, name='get_weights_old'),
    path('index/fetch-index-comp-weights', index_views.fetch_index_components_weights, name='fetch_index_components_weights'),
    path('index/fetch-index-daily', index_views.fetch_index_daily, name='fetch_index_daily'),

    path('tasks/check-task-status', index_views.check_task_status, name='check_task_status'),
]