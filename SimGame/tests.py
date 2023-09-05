from datetime import timezone, datetime

import pytest
from django.core.exceptions import ObjectDoesNotExist

from SimGame.models import SellerGoods, Goods, Balance, Transaction, Seller

from decimal import Decimal

from SimGame.forms import RegisterForm, LoginForm, ChangePriceOrCreateGoodForm

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from SimGame.views import calculate_demand, calculate_equilibrium_price


@pytest.mark.django_db
def test_login_view_get():
    client = Client()
    response = client.get(reverse('login'))
    assert response.status_code == 200
    assert 'login.html' in [template.name for template in response.templates]

@pytest.mark.django_db
def test_login_view_post_correct():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    response = client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
    assert response.status_code == 302
    assert response.url == reverse('home')
    assert '_auth_user_id' in client.session

@pytest.mark.django_db
def test_login_view_post_wrong():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    response = client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
    assert response.status_code == 200
    assert 'login.html' in [template.name for template in response.templates]
    assert 'Zły login lub hasło' in response.content.decode()


@pytest.mark.django_db
def test_register_view(client):
    url = reverse('register')
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], RegisterForm)
    data = {
        'username': 'testuser',
        'password1': 'testpassword',
        'password2': 'testpassword'
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert User.objects.filter(username='testuser').exists()


@pytest.mark.django_db
def test_register_view_get(client):
    url = reverse('register')  # Replace with the actual URL name
    response = client.get(url)

    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], RegisterForm)

@pytest.mark.django_db
def test_register_view_post(client):
    url = reverse('register')
    data = {
        'username': 'testuser',
        'password1': 'testpassword',
        'password2': 'testpassword'
    }
    response = client.post(url, data)

    assert response.status_code == 302
    assert User.objects.count() == 1
    assert User.objects.filter(username='testuser').exists()
    User.objects.filter(username='testuser').delete()
@pytest.mark.django_db
def test_home_view_get(client):
    url = reverse('home')
    response = client.get(url)

    assert response.status_code == 200
    assert 'home.html' in [template.name for template in response.templates]

@pytest.mark.django_db
def test_home_view_post(client):
    url = reverse('home')
    data = {

    }
    response = client.post(url, data)



@pytest.mark.django_db
def test_buy_good_view(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    seller = Seller.objects.create(name='Test Seller')
    good = Goods.objects.create(name='Test Good', price=10.00)
    sellergood = SellerGoods.objects.create(seller=seller, goods=good, quantity=1)
    client.login(username='testuser', password='testpassword')
    response = client.post(reverse('buy_good', kwargs={'sellergood_id': sellergood.id}))
    assert response.status_code == 302
    assert response.url == reverse('seller_detail', kwargs={'pk': seller.pk})
    updated_balance = Balance.objects.get(user=user)
    assert updated_balance.amount == Decimal('490.00')
    assert Transaction.objects.count() == 1
    transaction = Transaction.objects.first()
    assert transaction.user == user
    assert transaction.seller == seller
    assert transaction.goods == good
    assert transaction.quantity == 1
    assert transaction.type == 'buy'
    assert transaction.price == good.price
    with pytest.raises(ObjectDoesNotExist):
        SellerGoods.objects.get(id=sellergood.id)



@pytest.mark.django_db
def test_buy_good_view_money_too_low(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    seller = Seller.objects.create(name='Test Seller')
    good = Goods.objects.create(name='Test Good', price=510.00)
    sellergood = SellerGoods.objects.create(seller=seller, goods=good, quantity=1)
    client.login(username='testuser', password='testpassword')
    response = client.post(reverse('buy_good', kwargs={'sellergood_id': sellergood.id}))
    assert response.status_code == 302
    assert response.url == reverse('seller_detail', kwargs={'pk': seller.pk})
    updated_balance = Balance.objects.get(user=user)
    assert updated_balance.amount == Decimal('500.00')
    assert Transaction.objects.count() == 0
    assert SellerGoods.objects.filter(id=sellergood.id).exists()
    user.delete()
    seller.delete()
    good.delete()



@pytest.mark.django_db
def test_sell_good_view(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    seller = Seller.objects.create(name='Test Seller')
    good = Goods.objects.create(name='Test Good', price=10.00)
    sellergood = SellerGoods.objects.create(seller=seller, goods=good, quantity=1)
    client.login(username='testuser', password='testpassword')
    response = client.post(reverse('sell_good', kwargs={'sellergood_id': sellergood.id}))
    assert response.status_code == 302
    assert response.url == reverse('seller_detail', kwargs={'pk': seller.pk})
    updated_balance = Balance.objects.get(user=user)
    assert updated_balance.amount == Decimal('510.00')
    assert Transaction.objects.count() == 1
    transaction = Transaction.objects.first()
    assert transaction.user == user
    assert transaction.seller == seller
    assert transaction.goods == good
    assert transaction.quantity == 1
    assert transaction.type == 'sell'
    assert transaction.price == good.price
    updated_sellergood = SellerGoods.objects.get(id=sellergood.id)
    assert updated_sellergood.quantity == 2




@pytest.mark.django_db
def test_logout_view_get(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    url = reverse('logout')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('home')
    assert not response.wsgi_request.user.is_authenticated







@pytest.mark.django_db
def test_create_seller_valid(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    url = reverse('create_seller')
    response = client.post(url, {'seller_name': 'Dobre'})
    assert response.status_code == 302
    assert Seller.objects.filter(name='Dobre').exists()

@pytest.mark.django_db
def test_create_seller_invalid(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    url = reverse('create_seller')
    response = client.post(url, {'seller_name': 'zly123!'})
    assert response.status_code == 200
    assert 'error_message' in response.context
    assert not Seller.objects.filter(name='zly123!').exists()

@pytest.mark.django_db
def test_create_seller_non_authenticated():
    client = Client()
    url = reverse('create_seller')
    response = client.post(url, {'seller_name': 'Dobre'})
    assert response.status_code == 302
    assert not Seller.objects.filter(name='Dobre').exists()

@pytest.mark.django_db
def test_create_seller_non_authenticated():
    client = Client()
    url = reverse('create_seller')
    response = client.get(url, {'seller_name': 'Dobre'})
    assert response.status_code == 302
    assert not Seller.objects.filter(name='Dobre').exists()


@pytest.mark.django_db
def test_delete_good_view():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    sellergood = SellerGoods.objects.create(seller_id=1, goods_id=1, quantity=10)
    sellergood_id = sellergood.id
    url = reverse('delete_good', args=[sellergood_id])
    assert SellerGoods.objects.filter(id=sellergood_id).exists()
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('seller_detail', args=[sellergood.seller_id])
    assert not SellerGoods.objects.filter(id=sellergood_id).exists()


@pytest.mark.django_db
def test_delete_seller_view_auth():
    seller = Seller.objects.create(name='Test Seller')
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    url = reverse('delete_seller', args=[seller.pk])
    response = client.post(url)
    assert response.status_code == 302
    with pytest.raises(Seller.DoesNotExist):
        seller.refresh_from_db()


@pytest.mark.django_db
def test_delete_seller_nonauth():
    seller = Seller.objects.create(name='Test Seller')
    client = Client()
    url = reverse('delete_seller', args=[seller.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse('login'))
    seller.refresh_from_db()


@pytest.mark.django_db
def test_create_good_view_get():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    url = reverse('change_price_or_create_good')
    response_get = client.get(url)
    assert response_get.status_code == 200
    assert 'form' in response_get.context
    assert isinstance(response_get.context['form'], ChangePriceOrCreateGoodForm)

@pytest.mark.django_db
def test_create_good_view_post():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    url = reverse('change_price_or_create_good')
    data = {
        'good': '',
        'new_good_name': 'New Good',
        'price': '12.34'
    }
    response_post = client.post(url, data)
    assert response_post.status_code == 302
    assert Goods.objects.filter(name='New Good', price=Decimal('12.34')).exists()


@pytest.mark.django_db
def test_edit_good_view_get():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    existing_good = Goods.objects.create(name='Good', price=Decimal('20.00'))
    url = reverse('change_price_or_create_good')
    response_get = client.get(url)
    assert response_get.status_code == 200
    assert 'form' in response_get.context
    assert isinstance(response_get.context['form'], ChangePriceOrCreateGoodForm)

@pytest.mark.django_db
def test_edit_good_view_post():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    existing_good = Goods.objects.create(name='Good', price=Decimal('20.00'))
    url = reverse('change_price_or_create_good')
    data = {
        'good': existing_good.id,
        'new_good_name': '',
        'price': '25.00'
    }
    response_post = client.post(url, data)
    assert response_post.status_code == 302
    existing_good.refresh_from_db()
    assert existing_good.price == Decimal('25.00')


@pytest.mark.django_db
def test_change_non_auth_get():
    url = reverse('change_price_or_create_good')
    client = Client()
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith('/login/')

@pytest.mark.django_db
def test_change_non_auth_post():
    url = reverse('change_price_or_create_good')
    client = Client()
    data = {
        'good': '',
        'new_good_name': 'New Good',
        'price': '12.34'
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url.startswith('/login/')
@pytest.mark.django_db
def test_market_auth_get():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    response = client.get(reverse('market'))
    assert response.status_code == 200
    assert 'Market Overview' in response.content.decode()


@pytest.mark.django_db
def test_market_auth_post():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    response = client.get(reverse('market'))
    assert response.status_code == 200
    assert 'Market Overview' in response.content.decode()


@pytest.mark.django_db
def test_market_non_auth_get():
    client = Client()
    url = reverse('market')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith('/login/')

@pytest.mark.django_db
def test_market_non_auth_post():
    client = Client()
    url = reverse('market')
    response = client.post(url)
    assert response.status_code == 302
    assert response.url.startswith('/login/')
@pytest.mark.django_db
def test_player_list_view_authenticated_get():
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = Client()
    client.login(username='testuser', password='testpassword')
    url = reverse('player_list')
    response = client.get(url)
    assert response.status_code == 200
    assert 'players_data' in response.context
    assert len(response.context['players_data']) == 1
    assert 'testuser' in response.content.decode()
    assert '500' in response.content.decode()

@pytest.mark.django_db
def test_player_list_view_authenticated():
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = Client()
    client.login(username='testuser', password='testpassword')
    url = reverse('player_list')
    response = client.get(url)
    assert response.status_code == 200
    assert 'players_data' in response.context
    assert len(response.context['players_data']) == 1
    assert 'testuser' in response.content.decode()
    assert '500' in response.content.decode()


@pytest.mark.django_db
def test_player_list_non_auht():
    client = Client()
    url = reverse('player_list')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith('/login/')

@pytest.mark.django_db
def test_player_list_view_post():
    client = Client()
    url = reverse('player_list')
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_calculate_demand():
    user = User.objects.create_user(username='testuser', password='testpassword')
    seller = Seller.objects.create(name='Test Seller')
    good = Goods.objects.create(name='Test Good', price=10)
    Transaction.objects.create(
        goods=good,
        user=user,
        seller=seller,
        type='buy',
        quantity=5,
        price=Decimal('10.00'),
        date=datetime.now()
    )
    demand = calculate_demand(good)
    assert demand == 5

@pytest.mark.django_db
def test_calculate_equilibrium_price():
    good = Goods.objects.create(name='Test Good', price=10)
    intercept = 100
    coefficient = 0.5
    demand = 20
    equilibrium_price = calculate_equilibrium_price(intercept, coefficient, demand)
    assert equilibrium_price == Decimal('40.0')


