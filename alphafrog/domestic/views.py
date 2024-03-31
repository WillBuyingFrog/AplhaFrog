from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import tushare as ts
import json


@csrf_exempt  # 禁用CSRF保护
def get_weights(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        index_code = data.get('index_code')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        print(f'index_code: {index_code}, start_date: {start_date}, end_date: {end_date}')

        ts.set_token(settings.TUSHARE_TOKEN)
        pro = ts.pro_api()
        df = pro.index_weight(index_code=index_code, start_date=start_date, end_date=end_date)

        print(df)

        return JsonResponse({'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)