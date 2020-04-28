from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.cache import cache

from portfolio.models import Ticker

from backtester.pool import main_pool
from backtraderbd.data.bdshare import DseHisData as bds
from bdshare import get_current_trading_code

@shared_task
def back_testing():
    bd_ticker = Ticker.objects.all()
    main_pool(bd_ticker)

@shared_task
def download_daily_data():
    bd_stocks = get_current_trading_code()
    i=1
    for stock in bd_stocks['symbol']:
        bds.download_one_delta_data(stock)
        print('Process No: {0} - Stock Code: {1} :: Done'.format(i, stock))
        i +=1