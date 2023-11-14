from celery import shared_task
from management.commands.fetch_data import Command

@shared_task
def fetch_new_data_1m():
    Command().fetch_data(interval='1m')

@shared_task
def fetch_new_data_1h():
    Command().fetch_data(interval='1h')

@shared_task
def fetch_new_data_1d():
    Command().fetch_data(interval='1d')