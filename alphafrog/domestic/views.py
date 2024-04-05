from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult

import tushare as ts
import json
from datetime import datetime

from .tasks import get_index_components_and_weights

from domestic.models import IndexComponentWeight


@csrf_exempt
def get_weights(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        index_code = data.get('index_code')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        task = get_index_components_and_weights.delay(index_code, start_date, end_date)

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