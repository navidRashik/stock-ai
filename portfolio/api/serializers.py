from rest_framework import serializers

from portfolio.models import Portfolio, Transaction, Stock, TickerUpdate


class QuotesSerializer(serializers.ModelSerializer):
   class Meta:
        model = TickerUpdate
        fields = "__all__"


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('ticker', 'quantity')


class PortfolioSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    stocks = StockSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = ('id', 'name', 'cash', 'owner', 'stocks', 'created')
        read_only_fields = ('cash', 'created')


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('ticker', 'transaction_type', 'price', 'time', 'quantity', 'portfolio')
        read_only_fields = ('portfolio', 'time', 'price')
