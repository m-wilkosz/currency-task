from django.contrib import admin
from .models import ExchangeRate
from rangefilter.filters import DateTimeRangeFilterBuilder

class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('formatted_date', 'currency_pair', 'exchange_rate')
    search_fields = ['currency_pair', 'exchange_rate']
    list_filter = [
        ('date', DateTimeRangeFilterBuilder(title="Date",)),
        'currency_pair',
        'interval'
    ]

    def formatted_date(self, obj):
        return obj.date.strftime("%b. %d, %Y %H:%M:%S")
    formatted_date.admin_order_field = 'date'  # allows column order sorting
    formatted_date.short_description = 'Date'  # renames column head

admin.site.register(ExchangeRate, ExchangeRateAdmin)