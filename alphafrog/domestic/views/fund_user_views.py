from django.http import JsonResponse

from ..models.fund_models import FundInfo

def search_fund_info(request):
    if request.method == "GET":
        keyword = request.GET.get('keyword')
        page = request.GET.get('page')

        if len(keyword) < 2:
            return JsonResponse({'message': 'Keyword too short'}, status=400)

        name_query = FundInfo.objects.filter(name__contains=keyword)

        ts_code_query = FundInfo.objects.filter(ts_code__contains=keyword)

        fund_info = name_query | ts_code_query
        fund_info = fund_info.distinct()

        start = (int(page) - 1) * 10
        end = int(page) * 10

        data = [
            {
                'ts_code': index.ts_code,
                'name': index.name,
                'market': index.market
            } for index in fund_info[start:end]
        ]

        return JsonResponse({'data': data, 'message': 'success'}, status=200)

    else:

        return JsonResponse({'message': 'Invalid request'}, status=400)

