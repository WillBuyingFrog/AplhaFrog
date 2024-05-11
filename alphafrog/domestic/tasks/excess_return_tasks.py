from datetime import datetime

from celery import shared_task
from django.conf import settings
import tushare as ts


@shared_task(bind=True)
def calculate_cumulated_excess_return_fund_index(self, fund_ts_code, baseline, start_date, end_date, mode):

    from ..models.fund_models import FundNav
    from ..models.index_models import IndexDaily
    from .index_tasks import get_index_daily
    from .fund_tasks import get_fund_nav_single

    task_result = {
        'progress': 'initializing',
        'code': 1
    }
    self.update_state(state='PROGRESS', meta=task_result)

    ts.set_token(settings.TUSHARE_TOKEN)
    pro = ts.pro_api()

    baseline_comp_close_dict = {}
    baseline_comp_weight_dict = {}

    start_date_formatted = datetime.strptime(start_date, '%Y%m%d').date()
    end_date_formatted = datetime.strptime(end_date, '%Y%m%d').date()

    if mode == 1:
        # 模式1，从数据库中获取数据
        # 只抽取每日的净值数据，存入一个dict中，key为日期，value为净值
        fund_data = FundNav.objects.filter(ts_code=fund_ts_code,
                                           nav_date__range=(start_date_formatted, end_date_formatted))
        fund_data_dict = {data.nav_date: data.accum_nav for data in fund_data}

        # 按照交易日排序
        fund_data_dict = dict(sorted(fund_data_dict.items(), key=lambda x: x[0]))

        # print(f'fund_data_dict: {fund_data_dict}')

        for _id, index in enumerate(baseline):
            index_ts_code = index['ts_code']
            index_weight = index['weight']
            index_data = IndexDaily.objects.filter(ts_code=index_ts_code,
                                                   trade_date__range=(start_date_formatted, end_date_formatted))
            # 只抽取baseline中每个成分指数的收盘价，存入一个dict中，key为日期，value为收盘价
            index_data_dict = {data.trade_date: data.close for data in index_data}
            baseline_comp_close_dict[index_ts_code] = index_data_dict
            baseline_comp_weight_dict[index_ts_code] = index_weight
            # print(f'baseline_comp_close_dict: {baseline_comp_close_dict}')
            # print(f'baseline_comp_weight_dict: {baseline_comp_weight_dict}')

    elif mode == 2 or mode == 3:
        # 模式2或3，从tushare获取数据
        # 若模式为2，则表示从tushare获取数据后存入数据库
        if mode == 2:
            # 从tushare获取基金净值数据并保存到数据库中
            get_fund_nav_single(ts_code=fund_ts_code, start_date=start_date, end_date=end_date, mode=1)
            # 再进行一次数据库查询，获取数据
            fund_data = FundNav.objects.filter(ts_code=fund_ts_code,
                                               nav_date__range=(start_date_formatted, end_date_formatted))
            fund_data_dict = {data.nav_date: data.accum_nav for data in fund_data}
            # print(f'fund_data_dict: {fund_data_dict}')

            # 从tushare获取基准指数数据
            for _id, index in enumerate(baseline):
                index_ts_code = index['ts_code']
                index_weight = index['weight']
                # 从tushare获取基准指数数据
                get_index_daily(index_ts_code, start_date=start_date, end_date=end_date, mode=1)
                # 再进行一次数据库查询，获取数据
                index_data = IndexDaily.objects.filter(ts_code=index_ts_code,
                                                       trade_date__range=(start_date_formatted, end_date_formatted))
                index_data_dict = {data.trade_date: data.close for data in index_data}
                baseline_comp_close_dict[index_ts_code] = index_data_dict
                baseline_comp_weight_dict[index_ts_code] = index_weight
                # print(f'baseline_comp_close_dict: {baseline_comp_close_dict}')
                # print(f'baseline_comp_weight_dict: {baseline_comp_weight_dict}')
        else:
            fund_data = get_fund_nav_single(ts_code=fund_ts_code, start_date=start_date, end_date=end_date, mode=2)
            # 抽取出其中的data项
            fund_data = fund_data['data']
            fund_data_dict = {data.nav_date: data.accum_nav for data in fund_data}
            # print(f'fund_data_dict: {fund_data_dict}')

            for _id, index in enumerate(baseline):
                index_ts_code = index['ts_code']
                index_weight = index['weight']
                index_data = get_index_daily(index_ts_code, start_date=start_date, end_date=end_date, mode=2)
                # 抽取出其中的data项
                index_data = index_data['data']
                index_data_dict = {data.trade_date: data.close for data in index_data}
                baseline_comp_close_dict[index_ts_code] = index_data_dict
                baseline_comp_weight_dict[index_ts_code] = index_weight
                # print(f'baseline_comp_close_dict: {baseline_comp_close_dict}')
                # print(f'baseline_comp_weight_dict: {baseline_comp_weight_dict}')
    else:
        task_result['progress'] = 'mode参数错误'
        task_result['code'] = 0
        return task_result

    task_result['progress'] = "Finished fetching data"
    task_result['code'] = 1
    self.update_state(state='PROGRESS', meta=task_result)

    # 先计算第一个有记载交易日的比值，以便归一化
    first_trade_date = next(iter(fund_data_dict.keys()))

    # 计算每个交易日的baseline值
    # 考虑到数据可能缺失，所以按照基金净值数据中记载的日期遍历，计算比较基准值

    baseline_close_dict = {}
    for date in fund_data_dict.keys():
        baseline_close = 0
        for index_ts_code in baseline_comp_close_dict.keys():
            index_data_dict = baseline_comp_close_dict[index_ts_code]
            if date in index_data_dict:
                baseline_close += ((index_data_dict[date] / index_data_dict[first_trade_date])
                                   * baseline_comp_weight_dict[index_ts_code]) * 1000
        baseline_close_dict[date] = baseline_close

    # 计算累计超额收益
    # 考虑到数据可能缺失，所以对基金净值数据逐日遍历，计算CER
    cers = []

    alpha_T0 = fund_data_dict[first_trade_date] / baseline_close_dict[first_trade_date]

    for date in fund_data_dict.keys():
        # print(f'Calculating CER for {date}: {fund_data_dict[date]} / {baseline_close_dict[date]} / {alpha_T0}')
        # 如果baseline_close_dict[date]为0，则说明基准指数数据缺失，跳过这一天
        if baseline_close_dict[date] == 0:
            continue
        cer = fund_data_dict[date] / baseline_close_dict[date] / alpha_T0
        cers.append({
            'cer': cer,
            'trade_date': date,
            'baseline': baseline_close_dict[date],
            'fund_nav': fund_data_dict[date]
        })

    task_result['progress'] = 'Task complete'
    task_result['code'] = 0
    task_result['cers'] = cers

    self.update_state(state='SUCCESS', meta=task_result)

    return task_result

