from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings

from datetime import datetime

import tushare as ts


@shared_task(bind=True)
def get_stock_info(self, ts_code, name, exchange):

    ts.set_token(settings.TUSHARE_TOKEN)
    pro = ts.pro_api()
    from ..models.stock_models import StockInfo

    if exchange is not None:
        # 直接爬取指定交易所的数据
        df = pro.stock_basic(exchange=exchange, 
                             fields='ts_code,symbol,name,area,industry,fullname,enname,cnspell,market,exchange,curr_type,list_status,list_date,delist_date,is_hs,act_name,act_ent_type')
        
        # 如果没有找到，直接返回
        if df.empty:
            final_result = {
                'progress': f"Task complete, no stock found for {exchange}.",
                'code': -1
            }
            self.update_state(state='SUCCESS', meta=final_result)
            return final_result
        else:
            
            object_to_create = []
            for index, row in df.iterrows():
                object_to_create.append(
                    StockInfo(
                        ts_code=row['ts_code'],
                        symbol=row['symbol'],
                        name=row['name'],
                        area=row['area'],
                        industry=row['industry'],
                        fullname=row['fullname'],
                        enname=row['enname'],
                        cnspell=row['cnspell'],
                        market=row['market'],
                        exchange=row['exchange'],
                        curr_type=row['curr_type'],
                        list_status=row['list_status'],
                        list_date=datetime.strptime(row['list_date'], '%Y%m%d').date(),
                        delist_date=datetime.strptime(row['delist_date'], '%Y%m%d').date() if row['delist_date'] is not None else None,
                        is_hs=row['is_hs'],
                        act_name=row['act_name'],
                        act_ent_type=row['act_ent_type']
                    )
                )

                if len(object_to_create) >= 50:
                    StockInfo.objects.bulk_create(object_to_create)
                    object_to_create = []
                    print(f'{index}/{len(df)}')
            
            if object_to_create:
                StockInfo.objects.bulk_create(object_to_create)
            
            final_result = {
                'progress': f"Task complete, total {len(df)} records inserted.",
                'code': 0
            }
            self.update_state(state='SUCCESS', meta=final_result)
            return final_result
    elif ts_code is not None:
        # 优先使用ts_code搜索
        df = pro.stock_basic(ts_code=ts_code, name=name,
                            fields='ts_code,symbol,name,area,industry,fullname,enname,cnspell,market,exchange,curr_type,list_status,list_date,delist_date,is_hs,act_name,act_ent_type')
        # 如果没有找到，直接返回
        if df.empty:
            final_result = {
                'progress': f"Task complete, no stock found for {ts_code} or {name}.",
                'code': -1
            }
            self.update_state(state='SUCCESS', meta=final_result)
            return final_result
        else:
            # 结果必然只有一行，把这一行直接存入持久化后端
            obj = StockInfo(
                ts_code=df['ts_code'][0],
                symbol=df['symbol'][0],
                name=df['name'][0],
                area=df['area'][0],
                industry=df['industry'][0],
                fullname=df['fullname'][0],
                enname=df['enname'][0],
                cnspell=df['cnspell'][0],
                market=df['market'][0],
                exchange=df['exchange'][0],
                curr_type=df['curr_type'][0],
                list_status=df['list_status'][0],
                list_date=datetime.strptime(df['list_date'][0], '%Y%m%d').date(),
                delist_date=datetime.strptime(df['delist_date'][0], '%Y%m%d').date() if df['delist_date'][0] is not None else None,
                is_hs=df['is_hs'][0],
                act_name=df['act_name'][0],
                act_ent_type=df['act_ent_type'][0]
            )
            obj.save()
            final_result = {
                'progress': f"Task complete, total 1 record inserted.",
                'code': 0
            }
            self.update_state(state='SUCCESS', meta=final_result)
    elif name is not None:
        # 同样至多只有一条记录，没找到直接返回，找到了就把第一行记录存入持久化后端
        df = pro.stock_basic(name=name,
                            fields='ts_code,symbol,name,area,industry,fullname,enname,cnspell,market,exchange,curr_type,list_status,list_date,delist_date,is_hs,act_name,act_ent_type')
        if df.empty:
            final_result = {
                'progress': f"Task complete, no stock found for {name}.",
                'code': -1
            }
            self.update_state(state='SUCCESS', meta=final_result)
            return final_result
        else:
            obj = StockInfo(
                ts_code=df['ts_code'][0],
                symbol=df['symbol'][0],
                name=df['name'][0],
                area=df['area'][0],
                industry=df['industry'][0],
                fullname=df['fullname'][0],
                enname=df['enname'][0],
                cnspell=df['cnspell'][0],
                market=df['market'][0],
                exchange=df['exchange'][0],
                curr_type=df['curr_type'][0],
                list_status=df['list_status'][0],
                list_date=datetime.strptime(df['list_date'][0], '%Y%m%d').date(),
                delist_date=datetime.strptime(df['delist_date'][0], '%Y%m%d').date() if df['delist_date'][0] is not None else None,
                is_hs=df['is_hs'][0],
                act_name=df['act_name'][0],
                act_ent_type=df['act_ent_type'][0]
            )
            obj.save()
            final_result = {
                'progress': f"Task complete, total 1 record inserted.",
                'code': 0
            }
            self.update_state(state='SUCCESS', meta=final_result)
            return final_result
    else:
        final_result = {
            'progress': "Task complete, no search criteria provided.",
            'code': -1
        }
        self.update_state(state='SUCCESS', meta=final_result)
        return final_result