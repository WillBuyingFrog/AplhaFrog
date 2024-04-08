# index_tasks.py
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings

import tushare as ts
from datetime import datetime


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
    from ..models.index_models import IndexComponentWeight

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

    final_result = {
        'meta': {'output', f"Task complete, total {total} records inserted."}
    }
    self.update_state(state='SUCCESS', meta={'progress': f"Task complete, total {total} records inserted."})
    return final_result


@shared_task(bind=True)
def get_index_info(self, ts_code, name):
    
    ts.set_token(settings.TUSHARE_TOKEN)
    pro = ts.pro_api()

    # 优先使用ts_code搜索
    if ts_code is not None:
        df = pro.index_basic(ts_code=ts_code, name=name,
                            fields='ts_code,name,fullname,market,publisher,index_type,category,base_date,base_point,list_date,weight_rule,desc,exp_date')
        # 看有没有找到，如果没有再用name搜
        if df.empty:
            df = pro.index_basic(name=name,
                                fields='ts_code,name,fullname,market,publisher,index_type,category,base_date,base_point,list_date,weight_rule,desc,exp_date')
            # 如果还是没有，就直接返回
            if df.empty:
                final_result = {
                    'progress': f"Task complete, no index found for {ts_code} or {name}.",
                    'code': -1
                }
                self.update_state(state='SUCCESS', meta=final_result)
                return final_result
    else:
        # 没有传入ts_code，直接用name搜
        df = pro.index_basic(name=name,
                            fields='ts_code,name,fullname,market,publisher,index_type,category,base_date,base_point,list_date,weight_rule,desc,exp_date')
        if df.empty:
            final_result = {
                'progress': f"Task complete, no index found for {name}.",
                'code': -1
            }
            self.update_state(state='SUCCESS', meta=final_result)
            return final_result       

    from ..models.index_models import IndexInfo

    # print(df)

    counter = 0
    for index, row in df.iterrows():

        if row['exp_date'] is not None:
            row['exp_date'] = datetime.strptime(row['exp_date'], '%Y%m%d').date()

        obj = IndexInfo(
            ts_code=row['ts_code'],
            name=row['name'],
            fullname=row['fullname'],
            market=row['market'],
            publisher=row['publisher'],
            index_type=row['index_type'],
            category=row['category'],
            base_date=datetime.strptime(row['base_date'], '%Y%m%d').date(),
            base_point=row['base_point'],
            list_date=datetime.strptime(row['list_date'], '%Y%m%d').date(),
            weight_rule=row['weight_rule'],
            desc=row['desc'],
            exp_date=row['exp_date']
        )
        # 查找有没有ts_code重合的记录
        if IndexInfo.objects.filter(ts_code=row['ts_code']).exists():
            # 如果有，跳过这一条记录
            continue
        obj.save()
        counter += 1

    final_result = {
        'progress': f"Task complete, {counter} new index records saved.",
        'code': 1
    }
    self.update_state(state='SUCCESS', meta=final_result)
    return final_result


@shared_task(bind=True)
def get_index_daily(self, ts_code, trade_date=None, start_date=None, end_date=None):
    
    from ..models.index_models import IndexDaily

    if trade_date is not None:
        # 优先使用trade_date获取trade_date当天的数据
        ts.set_token(settings.TUSHARE_TOKEN)
        pro = ts.pro_api()
        df = pro.index_daily(ts_code=ts_code, trade_date=trade_date)

        # 如果输入的trade_date是非交易日，那么df应当为空，此时直接返回
        if df.empty:
            final_result = {
                'progress': f"Task complete, no data found for {ts_code} on {trade_date}.",
                'code': -1
            }
            self.update_state(state='SUCCESS', meta=final_result)
            return

        obj = IndexDaily(
            ts_code=df['ts_code'][0],
            trade_date=datetime.strptime(df['trade_date'][0], '%Y%m%d').date(),
            close=df['close'][0],
            open=df['open'][0],
            high=df['high'][0],
            low=df['low'][0],
            pre_close=df['pre_close'][0],
            change=df['change'][0],
            pct_chg=df['pct_chg'][0],
            vol=df['vol'][0],
            amount=df['amount'][0]
        )
        obj.save()

        final_result = {
            'progress': f"Task complete, index {ts_code} on {trade_date} saved.",
            'code': 1
        }
        return final_result
        
    elif start_date is not None and end_date is not None:
        # 获取从start_date到end_date之间的数据
        ts.set_token(settings.TUSHARE_TOKEN)
        pro = ts.pro_api()
        df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

        # print(df)

        if df.empty:
            final_result = {
                'progress': f"Task complete, no data found for {ts_code} from {start_date} to {end_date}.",
                'code': -1
            }
            self.update_state(state='SUCCESS', meta=final_result)
            return final_result

        slice_size = min(max(50, df.shape[0] // 10), 200)

        objects_to_insert = []

        for index, row in df.iterrows():
            obj = IndexDaily(
                ts_code=row['ts_code'],
                trade_date=datetime.strptime(row['trade_date'], '%Y%m%d').date(),
                close=row['close'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                pre_close=row['pre_close'],
                change=row['change'],
                pct_chg=row['pct_chg'],
                vol=row['vol'],
                amount=row['amount']
            )
            objects_to_insert.append(obj)

            if len(objects_to_insert) >= slice_size:
                IndexDaily.objects.bulk_create(objects_to_insert)
                objects_to_insert.clear()
        
        if len(objects_to_insert) > 0:
            IndexDaily.objects.bulk_create(objects_to_insert)
        
        final_result = {
            'progress': f"Task complete, total {df.shape[0]} records inserted.",
            'code': 1
        }

    self.update_state(state='SUCCESS', meta=final_result)
    return final_result