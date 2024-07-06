from django.db import models


class FundTransactionRecord(models.Model):
    TRANSACTION_TYPES = [
        ('buy', '买入'),
        ('auto_invest', '定投'),
        ('sell', '卖出'),
        ('dividend', '分红'),
        ('initial', '初始')
    ]

    transaction_time = models.DateField()  # 交易时间
    transaction_platform = models.CharField(max_length=50) # 交易平台
    fund_code = models.CharField(max_length=20)  # 基金代码
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)  # 交易金额
    transaction_nav = models.DecimalField(max_digits=10, decimal_places=4)  # 确认净值
    transaction_shares = models.DecimalField(max_digits=10, decimal_places=2)  # 确认份额数
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=2)  # 交易手续费
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)  # 交易类型

    class Meta:
        unique_together = ('transaction_time', 'fund_code', 'transaction_type')
        indexes = [
            models.Index(fields=['fund_code']),
        ]

    def __str__(self):
        return f"{self.fund_code} - {self.transaction_time} - {self.transaction_amount} - {self.transaction_type}"
