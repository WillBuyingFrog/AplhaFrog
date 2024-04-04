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


@csrf_exempt  # 禁用CSRF保护
def get_weights_old(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        index_code = data.get('index_code')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        print(f'index_code: {index_code}, start_date: {start_date}, end_date: {end_date}')

        ts.set_token(settings.TUSHARE_TOKEN)
        pro = ts.pro_api()
        df = pro.index_weight(index_code=index_code, start_date=start_date, end_date=end_date)

        # 获取数据一共多少行
        total = df.shape[0]
        objects_to_insert = []
        counter = 0

        # print(df)
        for index, row in df.iterrows():
            trade_date_str = row['trade_date']
            trade_date = datetime.strptime(trade_date_str, '%Y%m%d').date()
            obj = IndexComponentWeight(
                index_code=row['index_code'],
                con_code=row['con_code'],
                trade_date=trade_date,
                weight=row['weight']
            )

            objects_to_insert.append(obj)

            if len(objects_to_insert) >= 50:
                IndexComponentWeight.objects.bulk_create(objects_to_insert)
                objects_to_insert.clear()
                counter += 50
            

            
        
        if objects_to_insert:
            IndexComponentWeight.objects.bulk_create(objects_to_insert)



        return JsonResponse({'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)
    

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

        task_id = request.GET.get('task_id')
        task = AsyncResult(task_id)
        result = {
            'state': task.state,
            'result': task.result if task.successful() else None,
            'info': task.info if hasattr(task, 'info') else {},
        }

        return JsonResponse(result, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)