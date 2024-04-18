from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult

import tushare as ts
import json
from datetime import datetime

from ..tasks.fund_tasks import get_fund_info, get_fund_nav_all, get_fund_nav_single


@csrf_exempt
def fetch_fund_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ts_code = data.get('ts_code')
        market = data.get('market')
        status = data.get('status')

        task = get_fund_info.delay(ts_code, market, status)

        return JsonResponse({'task_id': task.id, 'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)
    

@csrf_exempt
def fetch_fund_nav(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ts_code = data.get('ts_code')
        nav_date = data.get('nav_date')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if ts_code is None:
            
            # 则nav_date必须为一个合法的YYYYMMDD字符串，或者说start_date和end_date都是合法的YYYYMMDD字符串
            if nav_date is None and (start_date is None or end_date is None):
                return JsonResponse({'message': 'ts_code is required'}, status=400)
            if nav_date is not None:
                try:
                    datetime.strptime(nav_date, '%Y%m%d')
                except ValueError:
                    return JsonResponse({'message': 'nav_date is not a valid date string'}, status=400)
                task = get_fund_nav_all.delay(nav_date)
            else:
                try:
                    datetime.strptime(start_date, '%Y%m%d')
                    datetime.strptime(end_date, '%Y%m%d')
                except ValueError:
                    return JsonResponse({'message': 'start_date or end_date is not a valid date string'}, status=400)
                task = get_fund_nav_all.delay(start_date=start_date, end_date=end_date)
        else:
            # 则nav_date必须为一个合法的YYYYMMDD字符串，或者说start_date和end_date都是合法的YYYYMMDD字符串
            if nav_date is None and (start_date is None or end_date is None):
                return JsonResponse({'message': 'ts_code is required'}, status=400)
            if nav_date is not None:
                try:
                    datetime.strptime(nav_date, '%Y%m%d')
                except ValueError:
                    return JsonResponse({'message': 'nav_date is not a valid date string'}, status=400)
                task = get_fund_nav_single.delay(ts_code, nav_date)
            else:
                try:
                    datetime.strptime(start_date, '%Y%m%d')
                    datetime.strptime(end_date, '%Y%m%d')
                except ValueError:
                    return JsonResponse({'message': 'start_date or end_date is not a valid date string'}, status=400)
                task = get_fund_nav_single.delay(ts_code, start_date=start_date, end_date=end_date)

        return JsonResponse({'task_id': task.id, 'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)