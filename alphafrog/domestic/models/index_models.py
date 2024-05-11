from django.db import models

# ------
# 指数相关实例
# ------

class IndexInfo(models.Model):
    ts_code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    fullname = models.CharField(max_length=100)
    market = models.CharField(max_length=20)
    publisher = models.CharField(max_length=50)
    index_type = models.CharField(max_length=20, null=True, blank=True)
    category = models.CharField(max_length=20, null=True, blank=True)
    base_date = models.DateField(null=True, blank=True)
    base_point = models.FloatField(null=True, blank=True)
    list_date = models.DateField(null=True, blank=True)
    weight_rule = models.CharField(max_length=200, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = '指数基本信息'
        verbose_name_plural = '指数基本信息'


class IndexDaily(models.Model):
    ts_code = models.CharField(max_length=20)
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

                
class IndexComponentWeight(models.Model):
    index_code = models.CharField(max_length=20)
    con_code = models.ForeignKey('StockInfo', on_delete=models.CASCADE)
    con_name = models.CharField()
    trade_date = models.DateField()
    weight = models.FloatField()

    class Meta:
        unique_together = (('index_code', 'con_code', 'trade_date'),)
        verbose_name = '指数成分股权重'
        verbose_name_plural = '指数成分股权重'