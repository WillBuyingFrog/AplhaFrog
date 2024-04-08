from django.urls import path
from .views import index_fetch_views

urlpatterns = [
    # path('index/get-weights-old', views.get_weights_old, name='get_weights_old'),
    path('index/fetch-index-info', index_fetch_views.fetch_index_info, name='fetch_index_info'),
    path('index/fetch-index-comp-weights', index_fetch_views.fetch_index_components_weights, name='fetch_index_components_weights'),
    path('index/fetch-index-daily', index_fetch_views.fetch_index_daily, name='fetch_index_daily'),

    path('tasks/check-task-status', index_fetch_views.check_task_status, name='check_task_status'),
]