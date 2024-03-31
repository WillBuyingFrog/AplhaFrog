from django.db import models

# 个股信息模型
class StockInfo(models.Model):
    ts_code = models.CharField(max_length=20, primary_key=True)
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    area = models.CharField(max_length=50)
    industry = models.CharField(max_length=50)
    fullname = models.CharField(max_length=100)
    enname = models.CharField(max_length=100, blank=True)
    cnspell = models.CharField(max_length=20, blank=True)
    market = models.CharField(max_length=10)
    exchange = models.CharField(max_length=10)
    curr_type = models.CharField(max_length=10)
    list_status = models.CharField(max_length=1)
    list_date = models.DateField()
    delist_date = models.DateField(null=True, blank=True)
    is_hs = models.CharField(max_length=1)
    act_name = models.CharField(max_length=100, blank=True)
    act_ent_type = models.CharField(max_length=50, blank=True)

# 个股日线行情模型
class StockDaily(models.Model):
    ts_code = models.ForeignKey(StockInfo, on_delete=models.CASCADE)
    trade_date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    pre_close = models.FloatField()
    change = models.FloatField()
    pct_chg = models.FloatField()
    vol = models.FloatField()
    amount = models.FloatField()

    class Meta:
        unique_together = (('ts_code', 'trade_date'),)
class IndexComponentWeight(models.Model):
    index_code = models.CharField(max_length=20)
    con_code = models.CharField(max_length=20)
    trade_date = models.DateField()
    weight = models.FloatField()

    class Meta:
        unique_together = (('index_code', 'con_code', 'trade_date'),)
        verbose_name = '指数成分股权重'
        verbose_name_plural = '指数成分股权重'


class IndexDaily(models.Model):
    ts_code = models.CharField(max_length=20, primary_key=True)
    trade_date = models.DateField()
    close = models.FloatField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    pre_close = models.FloatField(null=True, blank=True)
    change = models.FloatField(null=True, blank=True)
    pct_chg = models.FloatField(null=True, blank=True)
    vol = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = (('ts_code', 'trade_date'),)
        verbose_name = '指数日线行情'
        verbose_name_plural = '指数日线行情'


class IndexInfo(models.Model):
    ts_code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    fullname = models.CharField(max_length=100)
    market = models.CharField(max_length=20)
    publisher = models.CharField(max_length=50)
    index_type = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    base_date = models.DateField()
    base_point = models.FloatField()
    list_date = models.DateField()
    weight_rule = models.CharField(max_length=50)
    desc = models.TextField(blank=True)
    exp_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = '指数基本信息'
        verbose_name_plural = '指数基本信息'

