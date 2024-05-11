import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..tasks.excess_return_tasks import calculate_cumulated_excess_return_fund_index


@csrf_exempt
def get_cer_fund_indexes(request):
    if request.method == 'POST':
        # 获取传入参数
        data = json.loads(request.body)
        fund_ts_code = data.get('fund_ts_code')
        baseline = data.get('baseline')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        mode = data.get('mode')

        # 检查所有必需的参数是否都已提供
        if not all([fund_ts_code, baseline, start_date, end_date]):
            return JsonResponse({'msg': '缺少必需的参数'}, status=400)

        task = calculate_cumulated_excess_return_fund_index.delay(fund_ts_code, baseline, start_date, end_date, mode)

        return JsonResponse({'task_id': task.id, 'message': 'success'}, status=200)

    else:
        return JsonResponse({'msg': '请求方式错误'}, status=400)