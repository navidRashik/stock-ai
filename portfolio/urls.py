from django.urls import path

from .views import *

urlpatterns = [
    #path('login', LoginView.as_view(), name='login'),
    path('quotes/<tickers>/', LatestQuotesView.as_view(), name='quotes'),
    path('stocks/<tickers>/', StockDataView.as_view(), name='quotes'),
    path('stocks/tsv/<tickers>/', StockDataViewTSV.as_view(), name='quotestsv'),
    path('stocks/numpy/<tickers>/', StockDataViewNMP.as_view(), name='quotesnmp'),
]