from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..tasks.stock_tasks import get_stock_info

import json


@csrf_exempt
def fetch_stock_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ts_code = data.get('ts_code')
        name = data.get('name')
        exchange = data.get('exchange')

        task = get_stock_info.delay(ts_code, name, exchange)

        return JsonResponse({'task_id': task.id, 'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)