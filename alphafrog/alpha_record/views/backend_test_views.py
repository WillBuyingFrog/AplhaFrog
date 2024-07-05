from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..oss.oss_conn import establish_connection

import oss2

@csrf_exempt
def test_oss(request):
    if request.method == 'GET':
        # 只处理GET请求
        auth = establish_connection()

        return JsonResponse({'message': 'Please refer to Django console for more information.'}, status=200)

    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)

