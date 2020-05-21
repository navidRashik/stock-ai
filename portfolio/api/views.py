import ast
import datetime as dt
from bdshare import get_current_trade_data, get_basic_hist_data

from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse

from portfolio.models import Portfolio, Transaction, Stock, TickerUpdate
from portfolio.permissions import IsOwnerOrReadOnly, IsPortfolioOwnerOrReadOnly
from accounts.api.serializers import UserSerializer
from portfolio.api.serializers import TransactionSerializer, StockSerializer
from portfolio.api.serializers import PortfolioSerializer
from portfolio.api.serializers import QuotesSerializer


class GetQuotes(APIView):
    """
    /api/quote/<tickers>/
        GET: Get quote information on a list of tickers. Returns JSON response of a dict with keys
        being tickers and values being a dict of quote information.
    """
    def get(self, request, tickers):
        if (tickers=='all'):
            quotes = get_current_trade_data()
        else:
            quotes = get_current_trade_data(str(tickers))
        # if(quotes):
        #     quotes = quotes(orient='records', lines=True, compression='gzip')
        #     _, created = TickerUpdate.objects.update_or_create()
        #     dbquotes = TickerUpdate.objects.all()
        #     results = QuotesSerializer(dbquotes, many=True).data
        # else:
        #     dbquotes = TickerUpdate.objects.all()
        #     results = QuotesSerializer(dbquotes, many=True).data
        quotes = quotes.to_json(orient='records', compression='gzip')
        return Response(ast.literal_eval(quotes))


class GetStocks(APIView):
    """
    /api/stocks/<tickers>/
        GET: Get quote information on a list of tickers. Returns JSON response of a dict with keys
        being tickers and values being a dict of quote information.
    """
    def get(self, request, tickers):
        end = dt.datetime.now().date()
        if (tickers=='all'):
            his_data = get_basic_hist_data('2008-01-01', end)
        else:
            his_data = get_basic_hist_data('2008-01-01', end, code=str(tickers))
        his_data = his_data.to_json(orient='records', compression='gzip')
        return Response(ast.literal_eval(his_data))


class GetStocksTSV(APIView):
    """
    /api/stocks/<tickers>/
        GET: Get quote information on a list of tickers. Returns JSON response of a dict with keys
        being tickers and values being a dict of quote information.
    """
    def get(self, request, tickers):
        end = dt.datetime.now().date()
        if (tickers=='all'):
            his_data = get_basic_hist_data('2008-01-01', end)
        else:
            his_data = get_basic_hist_data('2008-01-01', end, code=str(tickers))
        his_data = his_data.to_csv(sep='\t', index=False, compression='gzip')
        return Response(his_data)

class PortfolioViewSet(viewsets.ModelViewSet):
    """
    /api/portfolios/
        GET: Get all portfolios. If a username query parameter is passed, then get that user's
        portfolios.
        POST: Create a portfolio. Must be authenticated. JSON payload must contain "name".

    /api/portfolios/<portfolio_id>/
        GET: Get one portfolio.
        PUT: Edit a portfolio (can only edit name). Must be authenticated as owner of portfolio.
        DELETE: Delete a portfolio. Must be authenticated as owner of portfolio.
    """
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,  # Unauthenticated users cannot POST
        IsOwnerOrReadOnly  # Authenticated users that don't own portfolio cannot edit it
    )

    # Request's user is saved as owner of portfolio
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # list can be filtered by username, otherwise return all portfolios
    def list(self, request):
        username = request.query_params.get('username', None)
        if username:
            user = User.objects.filter(username=username)
            queryset = Portfolio.objects.filter(owner=user)
        else:
            queryset = Portfolio.objects.all()
        serializer = PortfolioSerializer(queryset, many=True)
        return Response(serializer.data)


class TransactionsList(generics.ListCreateAPIView):
    """
    /api/portfolios/<portfolio_id>/transactions/
        GET: Get list of portfolio's transactions.
        POST: Create a transaction. Must be authenticated. JSON payload must contain:
            "ticker": Ticker of security you want to transact.
            "quantity": Number of units you want to transact.
            "transaction_type": Either "Buy" or "Sell"
    """
    serializer_class = TransactionSerializer
    permission_classes = (IsPortfolioOwnerOrReadOnly, )

    def get_queryset(self):
        p = get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'])
        # Return transactions in reverse order to get most recent
        # transactions first.
        return Transaction.objects.filter(portfolio=p)[::-1]

    def perform_create(self, serializer):

        # Assign request data to local variables
        portfolio = get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'])
        ticker = self.request.data['ticker'].upper()
        requested_quantity = int(self.request.data['quantity'])
        if requested_quantity <= 0:
            raise ValidationError("Cannot transact negative units.")
        transaction_type = self.request.data['transaction_type']

        # Get price of ticker and total transaction amount
        price = get_current_trade_data(ticker)[ticker]['price']
        transaction_amount = round(requested_quantity * price, 2)
        # Get the held stock if it already exists in the portfolio. Otherwise held_stock is None
        held_stock = portfolio.stocks.filter(ticker=ticker).first()

        if transaction_type == 'Buy':
            # Check if portfolio has sufficient funds to execute transaction
            if transaction_amount > portfolio.cash:
                raise ValidationError(
                    'Insufficient cash to buy {} shares of {}'.format(
                        requested_quantity,
                        ticker
                    )
                )
            portfolio.cash -= transaction_amount
            portfolio.save()
            if held_stock:
                held_stock.quantity += requested_quantity
                if held_stock.quantity == 0:
                    held_stock.delete()
                else:
                    held_stock.save()
            else:  # ticker doesn't exist in portfolio, create new Stock
                new_stock = Stock(
                    ticker=ticker,
                    quantity=requested_quantity,
                    portfolio=portfolio
                )
                new_stock.save()

        elif transaction_type == 'Sell':
            # If you hold more units than you want to sell, proceed.
            if held_stock and held_stock.quantity >= requested_quantity:
                portfolio.cash += transaction_amount
                portfolio.save()
                held_stock.quantity -= requested_quantity
                if held_stock.quantity == 0:
                    held_stock.delete()
                else:
                    held_stock.save()
            # Else we attempt to short and must check if equity > 150% short exposure
            else:
                short_exposure = portfolio.get_short_exposure()
                # If we don't have stock or have a short position in it, increase our short exposure
                # by transaction amount.
                if not held_stock or held_stock.quantity < 0:
                    short_exposure += transaction_amount
                # If we have stock but the sell transaction will move us into a short position,
                # add the remaining units to short exposure
                elif held_stock.quantity < requested_quantity:
                    short_exposure += (requested_quantity - held_stock.quantity) * price

                # If our equity is > 150% of short exposure, proceed with transaction
                equity = portfolio.get_market_value() + transaction_amount
                if short_exposure * 1.5 < equity:
                    portfolio.cash += transaction_amount
                    portfolio.save()
                    if held_stock:
                        held_stock.quantity -= requested_quantity
                        held_stock.save()
                    else:  # Create new short stock position if not held
                        new_stock = Stock(
                            ticker=ticker,
                            quantity=-requested_quantity,
                            portfolio=portfolio
                        )
                        new_stock.save()
                else:
                    raise ValidationError(
                        (
                            "This transaction will bring your equity to {0}, but your total "
                            "short exposure will be {1}. Your equity must be greater than "
                            "150% of your total short exposure to proceed."
                        ).format(equity, short_exposure)
                    )

        serializer.save(ticker=ticker, portfolio=portfolio, price=price)


class StocksList(generics.ListAPIView):
    """
    /api/portfolios/<portfolio_id>/stocks/
        GET: Get portfolio's stock holdings.
    """
    serializer_class = StockSerializer

    def get_queryset(self):
        p = get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'])
        return Stock.objects.filter(portfolio=p)


class UsersList(generics.ListAPIView):
    """
    /api/users/
        GET: Get all users.
    """
    serializer_class = UserSerializer

    def get_queryset(self):
        users = User.objects.all()
        return users
