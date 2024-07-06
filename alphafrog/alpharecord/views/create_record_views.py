from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..tasks.create_record_tasks import create_records_from_local_images


@csrf_exempt
def create_records_local(request):
    if request.method == 'POST':
        task = create_records_from_local_images.delay()

        return JsonResponse({
            'message': "Task created",
            'task_id': task.id
        }, status=200)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)
