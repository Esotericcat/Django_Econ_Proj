import pytest
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

# class LoginViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#
#     def test_get_login_page(self):
#         response = self.client.get(reverse('login'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'login.html')
#
#     def test_login_successful(self):
#         response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
#
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response.url, reverse('home'))
#         self.assertTrue('_auth_user_id' in self.client.session)
#
#     def test_login_failed(self):
#         response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'login.html')
#         self.assertContains(response, 'Zły login lub hasło')
#         self.assertFalse('_auth_user_id' in self.client.session)

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
def test_buy_good_view():
    client = Client()

    # Create an existing user
    existing_user = User.objects.create_user(username='existinguser', password='existingpassword')

    seller = Seller.objects.create(name='Test Seller')
    good = Goods.objects.create(name='Test Good', price=10.00)
    sellergood = SellerGoods.objects.create(seller=seller, goods=good, quantity=5)

    # Use the existing user's Balance object
    user_balance = Balance.objects.get(user=existing_user)

    client.login(username='existinguser', password='existingpassword')

    # Make sure the user's balance is enough for the purchase
    user_balance.amount = 50.00
    user_balance.save()

    response = client.post(reverse('buy_good', args=[sellergood.id]))
    assert response.status_code == 302


@pytest.mark.django_db
def test_sell_good_view():
    client = Client()
    existing_user = User.objects.create_user(username='existinguser', password='existingpassword')

    seller = Seller.objects.create(name='Test Seller')
    good = Goods.objects.create(name='Test Good', price=10.00)
    sellergood = SellerGoods.objects.create(seller=seller, goods=good, quantity=5)


    user_balance = Balance.objects.create(user=existing_user, amount=50.00)
    inventory_item = Inventory.objects.create(user=existing_user, goods=good, quantity=1)

    client.login(username='existinguser', password='existingpassword')

    response = client.post(reverse('sell_good', args=[sellergood.id]))
    assert response.status_code == 302

    # Check if the user's balance and inventory have been updated
    updated_balance = Balance.objects.get(user=existing_user)
    updated_inventory = Inventory.objects.get(user=existing_user, goods=good)

    assert updated_balance.amount == 60.00  # Updated balance after selling
    assert updated_inventory.quantity == 0  # Updated inventory after selling

    # Check if the seller's goods have been updated
    updated_sellergood = SellerGoods.objects.get(id=sellergood.id)
    assert updated_sellergood.quantity == 6  # Updated quantity after selling

