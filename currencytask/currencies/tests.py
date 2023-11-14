from django.test import TestCase
from currencies.management.commands.fetch_data import Command
from currencies.models import ExchangeRate, Currency
from unittest.mock import patch, MagicMock
import pandas as pd
from django.utils import timezone
from django.urls import reverse

class CurrenciesViewTests(TestCase):
    def setUp(self):
        # create some Currency test data
        Currency.objects.create(code='USD')
        Currency.objects.create(code='EUR')

        # create some ExchangeRate test data
        ExchangeRate.objects.create(
            date=timezone.now(),
            currency_pair='USDEUR',
            exchange_rate=1.2,
            interval='1m'
        )

    def test_currency_list(self):
        # test without filter
        response = self.client.get(reverse('currency_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('USD', response.content.decode())

        # test with filter
        response = self.client.get(reverse('currency_list') + '?filter_code=EUR')
        self.assertEqual(response.status_code, 200)
        self.assertIn('EUR', response.content.decode())

    def test_currency_pair(self):
        # test existing currency pair
        response = self.client.get(reverse('currency_pair', args=('USD', 'EUR')))
        self.assertEqual(response.status_code, 200)
        self.assertIn('USDEUR', response.content.decode())

        # test non-existing currency pair
        response = self.client.get(reverse('currency_pair', args=('AAA', 'BBB')))
        self.assertEqual(response.status_code, 404)

class FetchDataTest(TestCase):
    def setUp(self):
        pass

    @patch('yfinance.download')
    def test_successful_data_fetch_and_save(self, mock_download):
        # mock yfinance.download to return a dummy DataFrame
        mock_download.return_value = pd.DataFrame({
            'Close': {
                'EURUSD=X': pd.Series([1.2, 1.3], index=[pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')]),
                'GBPUSD=X': pd.Series([1.4, 1.5], index=[pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')]),
                'USDJPY=X': pd.Series([1.6, 1.7], index=[pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')]),
                'PLNUSD=X': pd.Series([1.8, 1.9], index=[pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')]),
            }
        })

        # execute the command
        command = Command()
        command.handle()

        # assert database entries were created
        self.assertTrue(ExchangeRate.objects.exists())

    @patch('yfinance.download')
    def test_unsupported_interval(self, mock_download):
        # execute the command with an unsupported interval and expect ValueError
        command = Command()
        with self.assertRaises(ValueError):
            command.fetch_data('unsupported_interval')

    @patch('yfinance.download')
    def test_retry_logic(self, mock_download):
        # simulate a failure on the first call and success on the second
        mock_download.side_effect = [Exception("Network Error"), MagicMock()]

        # execute the command
        command = Command()
        command.fetch_data('1d')

        # assert that the retry logic was triggered and the second call was successful
        self.assertEqual(mock_download.call_count, 2)

    @patch('yfinance.download')
    def test_error_handling(self, mock_download):
        # simulate an error
        mock_download.side_effect = Exception("Network Error")

        # execute the command
        command = Command()
        command.fetch_data('1d')

        # assert the command tried 3 retries (1+3 calls overall) before logging the final error
        self.assertEqual(mock_download.call_count, 4)