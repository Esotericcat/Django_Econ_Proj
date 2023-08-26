import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from SimGame.models import SellerGoods, Goods, Balance, Transaction, Seller, \
    Inventory  # Replace with your actual import paths
from decimal import Decimal

from SimGame.forms import RegisterForm, LoginForm


from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_login_view():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')

    
    response = client.get(reverse('login'))
    assert response.status_code == 200
    assert 'login.html' in [template.name for template in response.templates]


    response = client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
    assert response.status_code == 302
    assert response.url == reverse('home')
    assert '_auth_user_id' in client.session

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


