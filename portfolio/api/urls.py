from django.urls import path, include
from portfolio.api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('portfolios', views.PortfolioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('quote/<tickers>/', views.GetQuotes.as_view()),
    path('portfolios/<portfolio_id>/transactions/', views.TransactionsList.as_view(), name='portfolio-transactions'),
    path('portfolios/<portfolio_id>/stocks/', views.StocksList.as_view(), name='portfolio-stocks'),
    path('users/', views.UsersList.as_view()),
]