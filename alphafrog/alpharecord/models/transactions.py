from django.db import models


class FundTransactionRecord(models.Model):
    TRANSACTION_TYPES = [
        ('buy', '买入'),
        ('auto_invest', '定投'),
        ('sell', '卖出'),
        ('dividend', '分红'),
        ('initial', '初始'),
        ('transfer_sell', '转换卖出'),
        ('transfer_buy', '转换买入')
    ]

    transaction_time = models.DateTimeField()  # 交易时间
    transaction_platform = models.CharField(max_length=50, null=True)  # 交易平台
    transaction_ts_code = models.CharField(max_length=20, null=True)  # 基金代码
    transaction_fund_name = models.CharField(max_length=100, null=True)  # 基金名称
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)  # 交易金额
    transaction_nav = models.DecimalField(max_digits=10, decimal_places=4)  # 确认净值
    transaction_shares = models.DecimalField(max_digits=10, decimal_places=2)  # 确认份额数
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=2)  # 交易手续费
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)  # 交易类型
    transaction_transfer_link = models.IntegerField(null=True)  # 如果交易类型为转换卖出或转换买入，则记录转换对手方的交易记录的id

    class Meta:
        unique_together = ('transaction_time', 'transaction_ts_code', 'transaction_type')
        # indexes = [
        #     models.Index(fields=['transaction_ts_code']),
        # ]

    def __str__(self):
        return f"{self.transaction_ts_code} - {self.transaction_time} - {self.transaction_amount} - {self.transaction_type}"
