# index_tasks.py
from __future__ import absolute_import, unicode_literals
from celery import shared_task, current_task
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

    fetched_stock_ts_code = []

    for index, row in df.iterrows():
        trade_date_str = row['trade_date']
        trade_date = datetime.strptime(trade_date_str, '%Y%m%d').date()

        # 对每条权重记录，先查看有没有爬取过对应个股的信息
        from ..models.stock_models import StockInfo
        if row['con_code'] not in fetched_stock_ts_code:
            if not StockInfo.objects.filter(ts_code=row['con_code']).exists():
                # 爬取个股信息，不异步
                self.update_state(state='PROGRESS', meta={'progress': f"Getting stock info for {row['con_code']}."})
                from .stock_tasks import get_stock_info
                get_stock_info(ts_code=row['con_code'], name=None, exchange=None)
            fetched_stock_ts_code.append(row['con_code'])

        stock_obj = StockInfo.objects.get(ts_code=row['con_code'])
        obj = IndexComponentWeight(
            index_code=row['index_code'],
            con_code=stock_obj,
            con_name=stock_obj.name,
            trade_date=trade_date,
            weight=row['weight']
        )

        objects_to_insert.append(obj)

        if len(objects_to_insert) >= 50:
            IndexComponentWeight.objects.bulk_create(objects_to_insert)
            objects_to_insert.clear()
            counter += 50
            print(f'{counter}/{total}')
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
def get_index_info(self, ts_code, name, market):
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
    elif name is not None:
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
    elif market is not None:
        # 没有传入ts_code和name，直接用market搜
        df = pro.index_basic(market=market,
                             fields='ts_code,name,fullname,market,publisher,index_type,category,base_date,base_point,list_date,weight_rule,desc,exp_date')
        if df.empty:
            final_result = {
                'progress': f"Task complete, no index found for {market}.",
                'code': -1
            }
            self.update_state(state='SUCCESS', meta=final_result)
            return final_result
    else:
        final_result = {
            'progress': f"Task complete, no search criteria provided.",
            'code': -1
        }
        self.update_state(state='SUCCESS', meta=final_result)
        return final_result

    from ..models.index_models import IndexInfo

    counter = 0
    objects_to_create = []
    for index, row in df.iterrows():
        if row['exp_date'] is not None:
            row['exp_date'] = datetime.strptime(row['exp_date'], '%Y%m%d').date()
        if row['base_date'] is not None:
            row['base_date'] = datetime.strptime(row['base_date'], '%Y%m%d').date()
        if row['list_date'] is not None:
            row['list_date'] = datetime.strptime(row['list_date'], '%Y%m%d').date()

        obj = IndexInfo(
            ts_code=row['ts_code'],
            name=row['name'],
            fullname=row['fullname'],
            market=row['market'],
            publisher=row['publisher'],
            index_type=row['index_type'],
            category=row['category'],
            base_date=row['base_date'],
            base_point=row['base_point'],
            list_date=row['list_date'],
            weight_rule=row['weight_rule'],
            desc=row['desc'],
            exp_date=row['exp_date']
        )
        objects_to_create.append(obj)
        if len(objects_to_create) >= 50:
            IndexInfo.objects.bulk_create(objects_to_create, ignore_conflicts=True)
            objects_to_create.clear()
            counter += 50
            self.update_state(state='PROGRESS', meta={'progress': f'{counter} records saved.'})

    if len(objects_to_create)> 0:
        IndexInfo.objects.bulk_create(objects_to_create, ignore_conflicts=True)
        counter += len(objects_to_create)
        self.update_state(state='PROGRESS', meta={'progress': f'{counter} records saved.'})

    final_result = {
        'progress': f"Task complete, {counter} new index records saved.",
        'code': 1
    }
    self.update_state(state='SUCCESS', meta=final_result)
    return final_result


@shared_task(bind=True)
def get_index_daily(self, ts_code, trade_date=None, start_date=None, end_date=None, mode=1):
    from ..models.index_models import IndexDaily

    final_result = {
        'progress': "Initializing",
        'code': -1
    }

    if trade_date is not None:
        # 优先使用trade_date获取trade_date当天的数据
        ts.set_token(settings.TUSHARE_TOKEN)
        pro = ts.pro_api()
        df = pro.index_daily(ts_code=ts_code, trade_date=trade_date)

        # 如果输入的trade_date是非交易日，那么df应当为空，此时直接返回
        if df.empty:
            final_result['progress'] = f"Task complete, no data found for {ts_code} on {trade_date}."
            final_result['code'] = 0
            if current_task and (not current_task.request.called_directly):
                self.update_state(state='SUCCESS', meta=final_result)
            return final_result

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
        if mode == 1:
            obj.save()
            final_result['progress'] = f"Task complete, index {ts_code} on {trade_date} saved."
            final_result['code'] = 0
            if current_task:
                self.update_state(state='SUCCESS', meta=final_result)
            return final_result
        elif mode == 2:
            # 直接返回obj
            final_result['progress'] = f"Task complete, index {ts_code} on {trade_date} fetched."
            final_result['code'] = 0
            final_result['data'] = obj
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
            if current_task and (not current_task.request.called_directly):
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
            if mode == 1:
                # 此时需要保存到数据库中
                if len(objects_to_insert) >= slice_size:
                    IndexDaily.objects.bulk_create(objects_to_insert, ignore_conflicts=True)
                    objects_to_insert.clear()
        if mode == 1:
            if len(objects_to_insert) > 0:
                IndexDaily.objects.bulk_create(objects_to_insert, ignore_conflicts=True)

            final_result = {
                'progress': f"Task complete, total {df.shape[0]} records inserted.",
                'code': 1
            }
        elif mode == 2:
            final_result = {
                'progress': f"Task complete, total {df.shape[0]} records fetched.",
                'code': 1,
                'data': objects_to_insert
            }
    if mode == 1 and current_task and (not current_task.request.called_directly):
        self.update_state(state='SUCCESS', meta=final_result)
    return final_result
