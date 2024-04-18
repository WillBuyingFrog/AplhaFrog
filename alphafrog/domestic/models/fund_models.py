from django.db import models
from django.db.models import UniqueConstraint


class FundInfo(models.Model):
    ts_code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    management = models.CharField(max_length=100, blank=True)
    custodian = models.CharField(max_length=100, blank=True)
    fund_type = models.CharField(max_length=50, blank=True)
    found_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    list_date = models.DateField(blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    delist_date = models.DateField(blank=True, null=True)
    issue_amount = models.FloatField(blank=True, null=True)
    m_fee = models.FloatField(blank=True, null=True)
    c_fee = models.FloatField(blank=True, null=True)
    duration_year = models.FloatField(blank=True, null=True)
    p_value = models.FloatField(blank=True, null=True)
    min_amount = models.FloatField(blank=True, null=True)
    exp_return = models.FloatField(blank=True, null=True)
    benchmark = models.CharField(max_length=500, null=True)
    status = models.CharField(max_length=50, null=True)
    invest_type = models.CharField(max_length=50, null=True)
    type = models.CharField(max_length=50, null=True)
    trustee = models.CharField(max_length=100, null=True)
    purc_startdate = models.DateField(blank=True, null=True)
    redm_startdate = models.DateField(blank=True, null=True)
    market = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = '公募基金基本信息'
        verbose_name_plural = '公募基金基本信息'


class FundNav(models.Model):
    ts_code = models.CharField(max_length=20)
    ann_date = models.DateField(null=True, blank=True)
    nav_date = models.DateField(null=True, blank=True)
    unit_nav = models.FloatField(null=True, blank=True)
    accum_nav = models.FloatField(null=True, blank=True)
    accum_div = models.FloatField(null=True, blank=True)
    net_asset = models.FloatField(null=True, blank=True)
    total_netasset = models.FloatField(null=True, blank=True)
    adj_nav = models.FloatField(null=True, blank=True)
    update_flag = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name = '公募基金净值'
        verbose_name_plural = '公募基金净值'
        constraints = [
            UniqueConstraint(fields=['ts_code', 'nav_date'], name='unique_fund_nav'),
        ]


class FundHoldings(models.Model):
    ts_code = models.CharField(max_length=20)
    ann_date = models.CharField(max_length=20)
    end_date = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    mkv = models.FloatField()
    amount = models.FloatField()
    stk_mkv_ratio = models.FloatField()
    stk_float_ratio = models.FloatField()

    class Meta:
        verbose_name = '公募基金持仓信息'
        verbose_name_plural = '公募基金持仓信息'
        constraints = [
            UniqueConstraint(fields=['ts_code', 'ann_date', 'symbol'], name='unique_fund_holdings')
        ]


class FundManager(models.Model):
    ts_code = models.CharField(max_length=20)
    ann_date = models.DateField()
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    birth_year = models.CharField(max_length=4)
    edu = models.CharField(max_length=20)
    nationality = models.CharField(max_length=20)
    begin_date = models.DateField()
    end_date = models.DateField()
    resume = models.CharField(max_length=1000)

    class Meta:
        verbose_name = '公募基金基金经理'
        verbose_name_plural = '公募基金基金经理'