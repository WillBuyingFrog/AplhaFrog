from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult

import tushare as ts
import json
from datetime import datetime

from ..tasks.index_tasks import get_index_components_and_weights
from ..tasks.index_tasks import get_index_daily

from domestic.models import IndexComponentWeight


@csrf_exempt
def fetch_index_components_weights(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        index_code = data.get('index_code')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        task = get_index_components_and_weights.delay(index_code, start_date, end_date)

        return JsonResponse({'task_id': task.id, 'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)
    
@csrf_exempt
def fetch_index_daily(request):
    if request.method == 'POST':
            
        data = json.loads(request.body)
        ts_code = data.get('ts_code')
        trade_date = data.get('trade_date')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if ts_code is None:
            return JsonResponse({'message': 'ts_code is required'}, status=400)
        if trade_date is None and (start_date is None or end_date is None):
            return JsonResponse({'message': 'trade_date or start_date and end_date are required'}, status=400)
        
        task = get_index_daily.delay(ts_code, trade_date, start_date, end_date)

        return JsonResponse({'task_id': task.id, 'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)
    




def check_task_status(request):
    if request.method == 'GET':

        data = json.loads(request.body)
        task_id = data.get('task_id')
        task = AsyncResult(task_id)
        print(task.info)
        result = {
            'state': task.state,
            'result': task.result
        }

        return JsonResponse(result, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)