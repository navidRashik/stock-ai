from django.contrib import admin
from .models import Portfolio, Transaction, Stock, TickerUpdate, Ticker, Position

# Register your models here.
admin.site.register(Portfolio)
admin.site.register(Transaction)
admin.site.register(Stock)
admin.site.register(TickerUpdate)
admin.site.register(Ticker)
admin.site.register(Position)
