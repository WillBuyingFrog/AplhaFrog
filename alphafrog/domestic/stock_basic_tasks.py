# stock_basic_tasks.py
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings

import tushare as ts
from datetime import datetime


def get_stock_info(ts_code, name):
    pass


def get_stock_daily(ts_code, trade_date, start_date, end_date):
    pass