from django.urls import path
from .views import index_fetch_views, stock_fetch_views, fund_fetch_views
from .views import index_user_views
from .views import cumulated_excess_return_views

urlpatterns = [
    path('index/get-index-info', index_user_views.get_index_info, name='get_index_info'),
    path('index/search-index-info', index_user_views.search_index_info, name='search_index_info'),


    # path('index/get-weights-old', views.get_weights_old, name='get_weights_old'),
    path('index/fetch-index-info', index_fetch_views.fetch_index_info, name='fetch_index_info'),
    path('index/fetch-index-comp-weights', index_fetch_views.fetch_index_components_weights, name='fetch_index_components_weights'),
    path('index/fetch-index-daily', index_fetch_views.fetch_index_daily, name='fetch_index_daily'),

    path('stock/fetch-stock-info', stock_fetch_views.fetch_stock_info, name='fetch_stock_info'),

    path('fund/fetch-fund-info', fund_fetch_views.fetch_fund_info, name='fetch_fund_info'),
    path('fund/fetch-fund-nav', fund_fetch_views.fetch_fund_nav, name='fetch_fund_nav'),

    path('analysis/cer-fund-indexes', cumulated_excess_return_views.get_cer_fund_indexes, name='get_cer_fund_indexes'),

    path('tasks/check-task-status', index_fetch_views.check_task_status, name='check_task_status'),
]