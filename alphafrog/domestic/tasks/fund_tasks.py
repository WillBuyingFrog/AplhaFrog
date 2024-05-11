# fund_tasks.py
from __future__ import absolute_import, unicode_literals
from celery import shared_task, current_task
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


@shared_task(bind=True)
def get_fund_nav_single(self, ts_code, nav_date=None, start_date=None, end_date=None, mode=1):


    ts.set_token(settings.TUSHARE_TOKEN)
    pro = ts.pro_api()

    from ..models.fund_models import FundNav

    final_result = {
        'progress': "Initializing.",
        'code': -1
    }

    # 插入时on conflict do nothing
    if nav_date is not None:
        # 插入单条记录
        df = pro.fund_nav(ts_code=ts_code, nav_date=nav_date)
        if not df.empty:
            row = df.iloc[0]
            obj = FundNav(
                ts_code=row['ts_code'],
                ann_date=None if row['ann_date'] is None else datetime.strptime(row['ann_date'], '%Y%m%d').date(),
                nav_date=None if row['nav_date'] is None else datetime.strptime(row['nav_date'], '%Y%m%d').date(),
                unit_nav=row['unit_nav'],
                accum_nav=row['accum_nav'],
                accum_div=row['accum_div'],
                net_asset=row['net_asset'],
                total_netasset=row['total_netasset'],
                adj_nav=row['adj_nav'],
                update_flag=row['update_flag']
            )
            if mode == 1:
                # 模式1，保存到数据库，并记录任务完成的信息
                FundNav.objects.get_or_create(obj)
                final_result['progress'] = f"Task complete, fund {ts_code} on {nav_date} saved."
                final_result['code'] = 0
                self.update_state(state='SUCCESS', meta=final_result)
            elif mode == 2:
                # 如果不需要存储到数据库中，则返回从tushare获取的净值数据
                final_result['progress'] = f"Task complete, fund {ts_code} on {nav_date} fetched."
                final_result['code'] = 0
                final_result['data'] = obj
                return final_result
        else:
            final_result['progress'] = f"Task complete, no data found for {ts_code} on {nav_date}."
            final_result['code'] = 0
            self.update_state(state='SUCCESS', meta=final_result)
        return final_result

    else:
        # 获取从start_date到end_date之间的数据
        df = pro.fund_nav(ts_code=ts_code, start_date=start_date, end_date=end_date)

        if df.empty:
            final_result = {
                'progress': f"Task complete, no data found for {ts_code} from {start_date} to {end_date}.",
                'code': -1
            }
            if mode == 1 and current_task and (not current_task.request.called_directly):
                self.update_state(state='SUCCESS', meta=final_result)
            return final_result

        slice_size = min(max(50, df.shape[0] // 10), 200)

        objects_to_insert = []

        for index, row in df.iterrows():
            obj = FundNav(
                ts_code=row['ts_code'],
                ann_date=None if row['ann_date'] is None else datetime.strptime(row['ann_date'], '%Y%m%d').date(),
                nav_date=None if row['nav_date'] is None else datetime.strptime(row['nav_date'], '%Y%m%d').date(),
                unit_nav=row['unit_nav'],
                accum_nav=row['accum_nav'],
                accum_div=row['accum_div'],
                net_asset=row['net_asset'],
                total_netasset=row['total_netasset'],
                adj_nav=row['adj_nav'],
                update_flag=row['update_flag']
            )
            objects_to_insert.append(obj)

            if mode == 1:
                # 如果要将tushare爬取到的数据保存到数据库中，则这里需要分块保存
                if len(objects_to_insert) >= slice_size:
                    FundNav.objects.bulk_create(objects_to_insert, ignore_conflicts=True)
                    objects_to_insert.clear()
                    print(f'{index} records inserted.')

        if mode == 1:
            # 如果要将tushare爬取到的数据保存到数据库中，则这里需要保存剩余的数据
            if len(objects_to_insert) > 0:
                FundNav.objects.bulk_create(objects_to_insert, ignore_conflicts=True)
            final_result = {
                'progress': f"Task complete, total {df.shape[0]} records inserted.",
                'code': 1
            }
            if current_task and (not current_task.request.called_directly):
                self.update_state(state='SUCCESS', meta=final_result)
            return final_result
        elif mode == 2:
            # 如果不需要保存到数据库中，则直接返回从tushare获取的数据
            final_result['progress'] = f"Task complete, total {df.shape[0]} records fetched."
            final_result['code'] = 0
            final_result['data'] = objects_to_insert
            return final_result


@shared_task(bind=True)
def get_fund_nav_all(self, nav_date=None, start_date=None, end_date=None):
    
    ts.set_token(settings.TUSHARE_TOKEN)
    pro = ts.pro_api()

    from ..models.fund_models import FundNav
    if nav_date is not None:
        # 获取nav_date的所有公布的基金净值
        df = pro.fund_nav(nav_date=nav_date)
    else:
        # 获取从start_date到end_date的所有基金的公布净值
        df = pro.fund_nav(start_date=start_date, end_date=end_date)
    
    if df.empty:
        final_result = {
            'progress': f"Task complete, no data found for {nav_date}.",
            'code': -1
        }
        self.update_state(state='SUCCESS', meta=final_result)
        return final_result
    else:
        slice_size = min(max(50, df.shape[0] // 10), 200)

        objects_to_insert = []

        for index, row in df.iterrows():
            obj = FundNav(
                ts_code=row['ts_code'],
                ann_date=None if row['ann_date'] is None else datetime.strptime(row['ann_date'], '%Y%m%d').date(),
                nav_date=None if row['nav_date'] is None else datetime.strptime(row['nav_date'], '%Y%m%d').date(),
                unit_nav=row['unit_nav'],
                accum_nav=row['accum_nav'],
                accum_div=row['accum_div'],
                net_asset=row['net_asset'],
                total_netasset=row['total_netasset'],
                adj_nav=row['adj_nav'],
                update_flag=row['update_flag']
            )
            objects_to_insert.append(obj)

            if len(objects_to_insert) >= slice_size:
                FundNav.objects.bulk_create(objects_to_insert)
                objects_to_insert.clear()
                print(f'{index} records inserted.')
        
        if len(objects_to_insert) > 0:
            FundNav.objects.bulk_create(objects_to_insert)
        
        final_result = {
            'progress': f"Task complete, total {df.shape[0]} records inserted.",
            'code': 1
        }
        self.update_state(state='SUCCESS', meta=final_result)
        return final_result
