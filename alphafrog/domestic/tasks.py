# tasks.py
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings

import tushare as ts
from datetime import datetime

from domestic.models import IndexComponentWeight


@shared_task(bind=True)
def get_index_components_and_weights(self, index_code, start_date, end_date):

    task_id = self.request.id  # 获取当前任务ID

    ts.set_token(settings.TUSHARE_TOKEN)
    pro = ts.pro_api()
    df = pro.index_weight(index_code=index_code, start_date=start_date, end_date=end_date)

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
            # print(f'{counter}/{total}')
            self.update_state(state='PROGRESS', meta={'progress': f'{counter}/{total}'})
    
    if objects_to_insert:
        # print(f'{counter + len(objects_to_insert)}/{total}')
        IndexComponentWeight.objects.bulk_create(objects_to_insert)
    
    self.update_state(state='PROGRESS', meta={'progress': 'complete'})

