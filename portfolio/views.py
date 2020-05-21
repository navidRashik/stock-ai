import ast
import datetime as dt
from django.shortcuts import render
from bdshare import get_current_trade_data, get_basic_hist_data
from django.http import JsonResponse, HttpResponse
from django.views.generic import CreateView

# Create your views here.
class LatestQuotesView(CreateView):
    extra_context = {
        'title': 'Quotes'
    }

    def get(self, request, tickers):
        if (tickers=='all'):
            quotes = get_current_trade_data()
        else:
            quotes = get_current_trade_data(str(tickers))
        #quotes = quotes.to_json(orient='records', lines=True, compression='gzip')
        quotes = quotes.to_json(orient='records', compression='gzip')
        return JsonResponse(ast.literal_eval(quotes), safe=False)


class StockDataView(CreateView):
    extra_context = {
        'title': 'Stock Data'
    }

    def get(self, request, tickers):
        end = dt.datetime.now().date()
        if (tickers=='all'):
            his_data = get_basic_hist_data('2008-01-01', end)
        else:
            his_data = get_basic_hist_data('2008-01-01', end, code=str(tickers))
        his_data = his_data.to_json(orient='records', compression='gzip')
        return JsonResponse(ast.literal_eval(his_data), safe=False)


class StockDataViewTSV(CreateView):
    extra_context = {
        'title': 'Stock Data TSV'
    }

    def get(self, request, tickers):
        end = dt.datetime.now().date()
        if (tickers=='all'):
            his_data = get_basic_hist_data('2008-01-01', end)
        else:
            his_data = get_basic_hist_data('2008-01-01', end, code=str(tickers))
        his_data = his_data.to_csv(sep='\t', index=False, compression='gzip')
        return HttpResponse(his_data)


class StockDataViewNMP(CreateView):
    extra_context = {
        'title': 'Stock Data NMP'
    }

    def get(self, request, tickers):
        end = dt.datetime.now().date()
        if (tickers=='all'):
            his_data = get_basic_hist_data('2008-01-01', end)
        else:
            his_data = get_basic_hist_data('2008-01-01', end, code=str(tickers))
        his_data = his_data.to_numpy()
        return HttpResponse(his_data)
