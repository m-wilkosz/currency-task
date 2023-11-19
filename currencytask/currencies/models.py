from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=3, primary_key=True)

    def __str__(self):
        return self.code

class ExchangeRate(models.Model):
    date = models.DateTimeField()
    first_currency_code = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='exchange_first_code')
    second_currency_code = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='exchange_second_code')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)
    interval = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.date} {self.first_currency_code}{self.second_currency_code} {self.exchange_rate} {self.interval}"