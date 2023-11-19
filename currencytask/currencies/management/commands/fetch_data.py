import time
from django.core.management.base import BaseCommand
import pandas as pd
import yfinance as yf
from currencies.models import ExchangeRate, Currency
from datetime import timedelta
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.timezone import is_aware, make_aware, utc

class Command(BaseCommand):
    help = 'fetches initial currency exchange rate data and stores it in the database'

    # list of currency pairs to fetch data for
    currency_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'PLNUSD=X', 'EURCHF=X', 'SGD=X', 'EURJPY=X']

    # method to fetch data for a given interval
    def fetch_data(self, interval, retry=0, initial=False):
        self.stdout.write(f'fetching data for interval: {interval}...')

        # determine the time range for data fetching
        end_time = timezone.now()
        if interval == '1m':
            start_time = end_time - timedelta(hours=24) if initial else end_time - timedelta(minutes=30)
        elif interval == '1h':
            start_time = end_time - timedelta(days=7) if initial else end_time - timedelta(hours=2)
        elif interval == '1d':
            start_time = end_time - timedelta(days=365) if initial else end_time - timedelta(days=2)
        else:
            raise ValueError(f'unsupported interval: {interval}')

        try:
            data = yf.download(self.currency_pairs, interval=interval, start=start_time, end=end_time)

            # nested function to process and store the fetched data
            def process_data(data, interval):
                for currency_pair in self.currency_pairs:
                    try:
                        if currency_pair not in data['Close']:
                            raise KeyError(f'Data for {currency_pair} not found in {interval} data')

                        pair_data = data['Close'][currency_pair]

                        # iterate over the data and store it in the database
                        if isinstance(pair_data, pd.Series):
                            for time, exchange_rate in pair_data.items():
                                if pd.isna(exchange_rate):
                                    continue

                                # ensure that the time is timezone aware
                                if not is_aware(time):
                                    time = make_aware(time, utc)

                                if currency_pair[3:] == '=X':
                                    currency_pair = 'USD' + currency_pair[:-2]

                                # retrieve Currency instances
                                first_currency_code = Currency.objects.get(code=currency_pair[:3])
                                second_currency_code = Currency.objects.get(code=currency_pair[3:6])

                                # create record if it doesn't exist yet
                                ExchangeRate.objects.get_or_create(
                                    date=time,
                                    first_currency_code=first_currency_code,
                                    second_currency_code=second_currency_code,
                                    defaults={'exchange_rate': exchange_rate},
                                    interval=interval
                                )

                    except KeyError:
                        self.stderr.write(self.style.ERROR(f'Data for {currency_pair} not found in {interval} response'))
                    except ValueError as e:
                        self.stderr.write(self.style.ERROR(str(e)))
                    except IntegrityError as e:
                        self.stderr.write(self.style.ERROR(f'Error saving data for {currency_pair} in {interval}: {str(e)}'))

            # process the data for the given interval
            process_data(data, interval)

            self.stdout.write(self.style.SUCCESS('successfully fetched and stored data'))

        except Exception as e:
            if retry < 3:  # retry up to 3 times
                time.sleep(2 ** retry)  # exponential backoff
                self.stderr.write(self.style.WARNING(f'Retrying ({retry + 1}) due to error: {str(e)}'))
                self.fetch_data(interval, retry + 1)
            else:
                self.stderr.write(self.style.ERROR(f'Error fetching data after retries: {str(e)}'))

    # overriding the handle method to execute our custom logic
    def handle(self, *args, **kwargs):
        # create currencies if they don't exist yet
        currencies_to_add = ['USD', 'EUR', 'GBP', 'JPY', 'SGD', 'CHF', 'PLN']
        for code in currencies_to_add:
            Currency.objects.get_or_create(code=code)

        # fetch and process data for different intervals
        for interval in ['1m', '1h', '1d']:
            self.fetch_data(interval, initial=True)