from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings

import os

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


@csrf_exempt
def create_records_upload(request):
    if request.method == 'POST':
        if request.FILES.getlist('images'):
            uploaded_images = request.FILES.getlist('images')

            # 先清除临时文件夹中已有的图片
            for root, dirs, files in os.walk(settings.ALPHA_RECORD_TEMP_MEDIA_ROOT):
                for file in files:
                    os.remove(os.path.join(root, file))

            for uploaded_image in uploaded_images:
                # 获取文件名
                file_name = uploaded_image.name
                # 保存文件到临时文件夹
                saved_file_path = os.path.join(settings.ALPHA_RECORD_TEMP_MEDIA_ROOT, file_name)
                default_storage.save(saved_file_path, uploaded_image)

            task = create_records_from_local_images.delay()

            return JsonResponse({
                'message': "Task created",
                'task_id': task.id
            }, status=200)
        else:
            return JsonResponse({'message': 'Invalid request: images not uploaded'}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request'}, status=400)