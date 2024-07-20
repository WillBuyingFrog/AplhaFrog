from django.urls import path

from .views import backend_test_views
from .views import create_record_views
from .views import create_transaction_views

urlpatterns = [
    path('test_oss', backend_test_views.test_oss, name='test_oss'),
    path('create_records_local', create_record_views.create_records_local, name='create_record_local'),
    path('create_records', create_record_views.create_records_upload, name='create_records'),

    path('transactions/create/normal', create_transaction_views.create_normal_transaction,
         name='create_normal_transaction')

]