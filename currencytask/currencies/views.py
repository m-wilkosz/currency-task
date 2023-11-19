from django.http import JsonResponse
from .models import Currency, ExchangeRate

def currency_list(request):
    filter_code = request.GET.get('filter_code', '')
    sort_by = request.GET.get('sort', 'code')

    currencies = Currency.objects.all()

    if filter_code:
        currencies = currencies.filter(code__icontains=filter_code)

    if sort_by in ['code']:
        currencies = currencies.order_by(sort_by)
    else:
        currencies = currencies.order_by('code')

    data = [{"code": currency.code} for currency in currencies]

    return JsonResponse(data, safe=False)

def currency_pair(request, first_code, second_code):
    exchange_rate = ExchangeRate.objects.filter(
                                    first_currency_code__code=first_code
                                        ).filter(
                                    second_currency_code__code=second_code
                                        ).first()

    if not exchange_rate:
        return JsonResponse({"error": "currency pair not found"}, status=404)

    return JsonResponse({
        "currency_pair": first_code+second_code,
        "exchange_rate": exchange_rate.exchange_rate
    })