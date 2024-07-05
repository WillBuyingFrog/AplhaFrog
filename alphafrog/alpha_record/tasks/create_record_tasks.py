from celery import shared_task
from django.conf import settings

import openai

import os
import base64


# 将图片编码为base64发送
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


@shared_task(bind=True)
def create_records_from_local_images(self):
    # 从resources/alpha_record/prompts/get_fund_transaction_info.txt中加载prompt
    with open('resources/alpha_record/prompts/get_fund_transaction_info.txt', 'r') as prompt_file:
        prompt = prompt_file.read()

    primary_vlm = settings.PRIMARY_VLM

    if primary_vlm == 'qwen-vl-max' or primary_vlm == 'qwen-vl-plus':
        vlm_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        vlm_api_key = settings.DASHSCOPE_API_KEY
        model_name = "qwen-vl-max"
    else:
        vlm_base_url = "https://openrouter.ai/api/v1"
        vlm_api_key = settings.OPENROUTER_API_KEY
        model_name = "openai/gpt-4o"

    client = openai.OpenAI(
        base_url=vlm_base_url,
        api_key=vlm_api_key,
    )

    # 默认需要处理的图片都在resources/temp/alpha_record/upload下
    # 遍历这个目录下的图片
    for root, dirs, files in os.walk('resources/temp/alpha_record/upload'):
        for file in files:
            image_path = os.path.join(root, file)
            image_base64 = encode_image(image_path)
            print(f"正在处理图片：{image_path}")
            response = client.chat.completions.create(
                model=model_name,
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": prompt,
                    }, {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    }, ],
                }],
                temperature=0
            )
            print(f"测试响应：{response.choices[0].message.content}")
            task_result = {
                'progress': f"Processing image {image_path}",
                'code': 0
            }
            self.update_state(state='PROGRESS', meta=task_result)

    task_result = {
        'progress': 'All images processed',
        'code': 0
    }
    self.update_state(state='SUCCESS', meta=task_result)

    return task_result


