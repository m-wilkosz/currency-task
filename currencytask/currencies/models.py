from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=3)

    def __str__(self):
        return self.code

class ExchangeRate(models.Model):
    date = models.DateTimeField()
    currency_pair = models.CharField(max_length=6)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)
    interval = models.CharField(max_length=2)

    class Meta:
        unique_together = ('interval', 'date', 'currency_pair')

    def __str__(self):
        return f"{self.date} {self.currency_pair} {self.exchange_rate} {self.interval}"