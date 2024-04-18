# fund_tasks.py
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings

import tushare as ts
from datetime import datetime


@shared_task(bind=True)
def get_fund_info(self, ts_code, market, status='L'):

    ts.set_token(settings.TUSHARE_TOKEN)
    pro = ts.pro_api()
    from ..models.fund_models import FundInfo

    if ts_code is not None:
        
        # 先查询已连接的数据库中有没有ts_code对应的基金
        if not FundInfo.objects.filter(ts_code=ts_code).exists():
            # 爬取基金基本信息
            df = pro.fund_basic(ts_code=ts_code)
            if not df.empty:
                row = df.iloc[0]
                obj = FundInfo(
                    ts_code=row['ts_code'],
                    name=row['name'],
                    management=row['management'],
                    custodian=row['custodian'],
                    fund_type=row['fund_type'],
                    found_date= None if row['found_date'] is None else datetime.strptime(row['found_date'], '%Y%m%d').date(),
                    due_date=None if row['due_date'] is None else datetime.strptime(row['due_date'], '%Y%m%d').date(),
                    list_date=None if row['list_date'] is None else datetime.strptime(row['list_date'], '%Y%m%d').date(),
                    issue_date=None if row['issue_date'] is None else datetime.strptime(row['issue_date'], '%Y%m%d').date(),
                    delist_date=None if row['delist_date'] is None else datetime.strptime(row['delist_date'], '%Y%m%d').date(),
                    issue_amount=row['issue_amount'],
                    m_fee=row['m_fee'],
                    c_fee=row['c_fee'],
                    duration_year=row['duration_year'],
                    p_value=row['p_value'],
                    min_amount=row['min_amount'],
                    exp_return=row['exp_return'],
                    benchmark=row['benchmark'],
                    status=row['status'],
                    invest_type=row['invest_type'],
                    type=row['type'],
                    trustee=row['trustee'],
                    purc_startdate=None if row['purc_startdate'] is None else datetime.strptime(row['purc_startdate'], '%Y%m%d').date(),
                    redm_startdate=None if row['redm_startdate'] is None else datetime.strptime(row['redm_startdate'], '%Y%m%d').date(),
                    market=row['market']
                )
                obj.save()
                final_result = {
                    'progress': f"Task complete, fund {ts_code} added.",
                    'code': 0
                }
                self.update_state(state='SUCCESS', meta=final_result)
            else:
                final_result = {
                    'progress': f"Task complete, no fund found for {ts_code}.",
                    'code': -1
                }
                self.update_state(state='SUCCESS', meta=final_result)
            return final_result
        else:
            final_result = {
                'progress': f"Task complete, fund {ts_code} already exists.",
                'code': 0
            }
            self.update_state(state='SUCCESS', meta=final_result)
            return final_result
    else:
        # 没有传入ts_code，按照market和status爬取
        df = pro.fund_basic(market=market, status=status)

        slice_size = min(max(50, df.shape[0] // 10), 200)

        objects_to_create = []

        for index, row in df.iterrows():
            obj = FundInfo(
                    ts_code=row['ts_code'],
                    name=row['name'],
                    management=row['management'],
                    custodian=row['custodian'],
                    fund_type=row['fund_type'],
                    found_date= None if row['found_date'] is None else datetime.strptime(row['found_date'], '%Y%m%d').date(),
                    due_date=None if row['due_date'] is None else datetime.strptime(row['due_date'], '%Y%m%d').date(),
                    list_date=None if row['list_date'] is None else datetime.strptime(row['list_date'], '%Y%m%d').date(),
                    issue_date=None if row['issue_date'] is None else datetime.strptime(row['issue_date'], '%Y%m%d').date(),
                    delist_date=None if row['delist_date'] is None else datetime.strptime(row['delist_date'], '%Y%m%d').date(),
                    issue_amount=row['issue_amount'],
                    m_fee=row['m_fee'],
                    c_fee=row['c_fee'],
                    duration_year=row['duration_year'],
                    p_value=row['p_value'],
                    min_amount=row['min_amount'],
                    exp_return=row['exp_return'],
                    benchmark=row['benchmark'],
                    status=row['status'],
                    invest_type=row['invest_type'],
                    type=row['type'],
                    trustee=row['trustee'],
                    purc_startdate=None if row['purc_startdate'] is None else datetime.strptime(row['purc_startdate'], '%Y%m%d').date(),
                    redm_startdate=None if row['redm_startdate'] is None else datetime.strptime(row['redm_startdate'], '%Y%m%d').date(),
                    market=row['market']
                )
            objects_to_create.append(obj)

            if len(objects_to_create) == slice_size:
                FundInfo.objects.bulk_create(objects_to_create)
                objects_to_create = []
                print(f'{index} records inserted.')

        if len(objects_to_create) > 0:
            FundInfo.objects.bulk_create(objects_to_create)
            print(f'{len(objects_to_create)} records inserted.')
        
        final_result = {
            'progress': f"Task complete, total {df.shape[0]} records inserted.",
            'code': 1
        }
        self.update_state(state='SUCCESS', meta=final_result)
        return final_result