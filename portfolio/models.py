from django.utils.translation import gettext_lazy as _
from django.db import models
from accounts.models import User


class Portfolio(models.Model):
    """
    A portfolio belongs to a User
    """

    name = models.CharField(_("Protfolio owner"), max_length=100)
    cash = models.FloatField(_("Cash"), default=100000)
    owner = models.ForeignKey(
        User,
        related_name="portfolios",
        verbose_name=_("Owner"),
        on_delete=models.CASCADE,
    )

    def get_market_value(self):
        """
        Return portfolio's market value. This is sum of cash and market value of long positions.

        Returns:
            float: portfolio's market value
        """
        market_value = self.cash
        long_stocks = [stock for stock in self.stocks.all() if stock.quantity > 0]
        if long_stocks:
            long_stocks_tickers = ",".join(
                [stock.ticker.symbol for stock in long_stocks]
            )
            long_stocks_quote = get_current_trade_data(long_stocks_tickers)
            for stock in long_stocks:
                market_value += long_stocks_quote[stock.ticker]["ltp"] * stock.quantity
        return market_value


class Ticker(models.Model):
    """ """

    symbol = models.CharField(_("SYMBOL"), max_length=15)


class TickerUpdate(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    ltp = models.FloatField(blank=True)
    high = models.FloatField(blank=True)
    low = models.FloatField(blank=True)
    close = models.FloatField(blank=True)
    ycp = models.FloatField(blank=True)
    change = models.FloatField(blank=True)
    trade = models.IntegerField()
    value = models.FloatField(blank=True)
    volume = models.IntegerField()
    updated_at = models.DateTimeField(_("Updated at"), auto_now_add=True)


class Stock(models.Model):
    """
    Stock belongs to a Portfolio
    """

    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name="tickers")
    quantity = models.IntegerField()
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="stocks"
    )


class Transaction(models.Model):
    """
    Transection is belongs to a Portfolio
    """

    TRANSACTION_TYPE = (("Buy", "Buy"), ("Sell", "Sell"))

    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=4)
    price = models.FloatField(blank=True)
    time = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)


class Position(models.Model):
    """
    Position is a record of a Portfolio's stock holding on a given date
    """

    datetime = models.DateTimeField(auto_now_add=True)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    units = models.IntegerField()
    price = models.FloatField()
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)


# Must import after model definitions because of circular import error
from bdshare import get_current_trade_data
