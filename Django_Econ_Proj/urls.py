"""
URL configuration for Django_Econ_Proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from SimGame import views
from SimGame.views import SellerDetail, GoodDetail, DeleteSellerView, EditSellerGoodsPageView, DeleteGoodView, \
    CreateSeller, ChangePriceOrCreateGoodView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Home.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('player_list/', views.PlayerList.as_view(), name='player_list'),
    path('vendor_list/', views.VendorList.as_view(), name='vendor_list'),
    path('delete/<int:seller_id>/', DeleteSellerView.as_view(), name='delete_seller'),
    path('edit_seller_goods/', EditSellerGoodsPageView.as_view(), name='edit_seller_goods_page'),
    path('seller/<int:pk>/', SellerDetail.as_view(), name='seller_detail'),
    path('buy/<int:sellergood_id>/', views.BuyGood.as_view(), name='buy_good'),
    path('sell/<int:sellergood_id>/', views.SellGood.as_view(), name='sell_good'),
    path('market/',views.MarketView.as_view(), name='market'),
    path('delete_good/<int:sellergood_id>/', DeleteGoodView.as_view(), name='delete_good'),
    path('create_seller/', CreateSeller.as_view(), name='create_seller'),
    path('change_price_or_create_good/', ChangePriceOrCreateGoodView.as_view(), name='change_price_or_create_good'),





    path('good_detail/<int:pk>/', GoodDetail.as_view(), name='good_detail'),


]
