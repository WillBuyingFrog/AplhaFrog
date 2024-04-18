from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult

import tushare as ts
import json
from datetime import datetime

from ..tasks.fund_tasks import get_fund_info


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