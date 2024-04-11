import json

from django.http import JsonResponse
from ..models.index_models import IndexInfo, IndexDaily, IndexComponentWeight


def get_index_info(request):
    if request.method == 'GET':
        data = json.loads(request.body)
        page = data.get('page')

        # 获取第(page-1)*10到page*10条数据
        start = (int(page) - 1) * 10
        end = int(page) * 10
        index_info = IndexInfo.objects.all()[start:end]

        data = []
        for index in index_info:
            data.append({
                'ts_code': index.ts_code,
                'name': index.name,
                'market': index.market,
                'publisher': index.publisher,
                'index_type': index.index_type,
                'category': index.category,
                'base_date': index.base_date,
                'base_point': index.base_point,
                'list_date': index.list_date,
                'weight_rule': index.weight_rule,
                'desc': index.desc
            })
        
        return JsonResponse({'data': data, 'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)
    

def get_index_components_weights(request):
    if request.method == 'GET':
        data = json.loads(request.body)
        index_code = data.get('index_code')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        index_components_weights = IndexComponentWeight.objects.filter(index_code=index_code, trade_date__gte=start_date, trade_date__lte=end_date)

        data = []
        for index in index_components_weights:
            data.append({
                'index_code': index.index_code,
                'trade_date': index.trade_date,
                'con_code': index.con_code,
                'con_name': index.con_name,
                'con_weight': index.con_weight
            })
        
        return JsonResponse({'data': data, 'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)


def get_index_daily(request):
    if request.method == 'GET':
        data = json.loads(request.body)
        ts_code = data.get('ts_code')
        trade_date = data.get('trade_date')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if ts_code is None:
            return JsonResponse({'message': 'ts_code is required'}, status=400)
        if trade_date is None and (start_date is None or end_date is None):
            return JsonResponse({'message': 'trade_date or start_date and end_date are required'}, status=400)
        
        if trade_date is not None:
            index_daily = IndexDaily.objects.filter(ts_code=ts_code, trade_date=trade_date)
        if start_date is not None and end_date is not None:
            index_daily = IndexDaily.objects.filter(ts_code=ts_code, trade_date__gte=start_date, trade_date__lte=end_date)
        
        data = []
        for index in index_daily:
            data.append({
                'ts_code': index.ts_code,
                'trade_date': index.trade_date,
                'close': index.close,
                'open': index.open,
                'high': index.high,
                'low': index.low,
                'pre_close': index.pre_close,
                'change': index.change,
                'pct_chg': index.pct_chg,
                'vol': index.vol,
                'amount': index.amount
            })
        
        return JsonResponse({'data': data, 'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)