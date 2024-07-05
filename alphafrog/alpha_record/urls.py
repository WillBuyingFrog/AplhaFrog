from django.urls import path

from .views import backend_test_views
from .views import create_record_views

urlpatterns = [
    path('test_oss', backend_test_views.test_oss, name='test_oss'),
    path('create_records_local', create_record_views.create_records_local, name='create_record_local')
]