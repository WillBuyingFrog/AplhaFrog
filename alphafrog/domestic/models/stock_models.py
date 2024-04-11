from django.db import models

from .index_models import IndexComponentWeight

# 个股信息模型
class StockInfo(models.Model):
    ts_code = models.CharField(max_length=20, primary_key=True)
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    area = models.CharField(max_length=50, null=True)
    industry = models.CharField(max_length=50, null=True)
    fullname = models.CharField(max_length=100, null=True)
    enname = models.CharField(max_length=100, blank=True, null=True)
    cnspell = models.CharField(max_length=20, blank=True)
    market = models.CharField(max_length=10)
    exchange = models.CharField(max_length=10)
    curr_type = models.CharField(max_length=10)
    list_status = models.CharField(max_length=1)
    list_date = models.DateField()
    delist_date = models.DateField(null=True, blank=True)
    is_hs = models.CharField(max_length=1, null=True)
    act_name = models.CharField(max_length=100, blank=True, null=True)
    act_ent_type = models.CharField(max_length=50, blank=True, null=True)
    index_component_weights = models.ManyToManyField(IndexComponentWeight, related_name='stock_infos')

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

