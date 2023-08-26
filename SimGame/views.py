import decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from decimal import Decimal
from django.shortcuts import render
import random
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from SimGame.forms import LoginForm, RegisterForm, ChooseUserForm
from SimGame.models import Balance, SellerGoods, Seller, Transaction, Inventory, Goods



def calculate_demand(good):

    total_quantity_sold = Transaction.objects.filter(goods=good, type='sell').aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_quantity_bought = Transaction.objects.filter(goods=good, type='buy').aggregate(Sum('quantity'))['quantity__sum'] or 0
    demand = total_quantity_bought - total_quantity_sold
    demand = max(demand, 0)

    return demand





def calculate_equilibrium_price(intercept, coefficient, demand):
    equilibrium_price = (intercept - demand) / coefficient
    return max(equilibrium_price, 0)

from decimal import Decimal


def adjust_price_based_on_equilibrium(good, transaction_type):
    first_transaction = Transaction.objects.filter(goods=good).order_by('date').first()
    if first_transaction:
        intercept = Decimal(str(first_transaction.price))
    else:
        intercept = Decimal('0.00')

    demand = calculate_demand(good)
    num_sellers = Seller.objects.count()
    coefficient = Decimal('0.5') - (num_sellers * Decimal('0.02'))

    damping_factor = Decimal('0.1')

    current_price = good.price
    price_difference = 0

    if transaction_type == 'buy':
        demand = max(demand, 0)
        equilibrium_price = calculate_equilibrium_price(intercept, coefficient, demand)
        price_difference = equilibrium_price - current_price
        damping_factor *= Decimal('1.1')
    elif transaction_type == 'sell':
        demand = min(demand, 0)
        equilibrium_price = calculate_equilibrium_price(intercept, coefficient, -demand)
        price_difference = current_price - equilibrium_price
        damping_factor *= Decimal('0.9')

    price_change = price_difference * damping_factor
    new_price = current_price + price_change

    if new_price >= Decimal('0.00'):
        good.price = new_price
        good.save()
    else:
        good.price = Decimal('0.00')
        good.save()
def generate_simulation_graph(good_id):
    transactions = Transaction.objects.filter(goods_id=good_id).order_by('date')
    seller_goods = SellerGoods.objects.filter(goods_id=good_id).order_by('seller', 'goods')

    price_data = [transaction.price for transaction in transactions]
    demand_data = []
    supply_data = [sg.quantity for sg in seller_goods]
    current_demand = 0

    for transaction in transactions:
        current_demand += transaction.goods.cumulative_demand
        demand_data.append(current_demand)
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(price_data, label='Price')
    plt.xlabel('Number of Transactions')
    plt.ylabel('Price')
    plt.title(f'Price Simulation Over Time for Good {good_id}')
    plt.legend()


    plt.subplot(2, 1, 2)
    plt.plot(demand_data, label='Demand', color='orange')
    plt.plot(supply_data, label='Supply', color='blue')
    plt.xlabel('Number of Transactions')
    plt.ylabel('Demand/Supply')
    plt.title(f'Demand and Supply Simulation Over Time for Good {good_id}')
    plt.legend()

    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    plot_image_base64 = base64.b64encode(buffer.read()).decode()
    return plot_image_base64
class LoginView(View):
    def get(self, request):
            return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next', 'home')
            return redirect(redirect_url)
        return render(request, 'login.html', {'error': 'Zły login lub hasło'})


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('home')



class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'form.html', {'form': form})
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.set_password(form.cleaned_data['password1'])
            user.save()

            return redirect('login')
        return render(request, 'form.html', {'form': form})



class Home(View):
    def get(self, request):
        return render(request, 'home.html')



class MarketView(View):
    def get(self, request):
        goods_list = Goods.objects.all()
        transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:10]
        context = {'goods_list': goods_list, 'transactions': transactions}
        return render(request,'marketplace.html', context)


class ChangeGoodsView(View):
    template_name = 'change.html'

    def get(self, request):
        seller_goods = SellerGoods.objects.all()
        return render(request, self.template_name, {'seller_goods': seller_goods})

    def post(self, request):
        seller_goods_id = request.POST.get('seller_goods')
        new_price = request.POST.get('price')
        new_quantity = request.POST.get('quantity')

        if seller_goods_id and new_price is not None and new_quantity is not None:
            seller_goods = SellerGoods.objects.get(pk=seller_goods_id)
            seller_goods.goods.price = new_price
            seller_goods.quantity = new_quantity
            seller_goods.goods.save()
            seller_goods.save()

        return redirect('change_goods')

class PlayerDetail(View):
    def get(self, request):

        inventory = Inventory.objects.filter(user=request.user).select_related('goods')
        return render(request, 'player_detail.html', {'inventory': inventory})

class PlayerList(View):
    def get(self, request):
        user_balances = Balance.objects.all()
        players_data = [{'name': balance.user.username, 'balance': balance.amount} for balance in user_balances]
        return render(request, 'player_list.html', {'players_data': players_data})
class VendorList(View):
    def get(self, request):
        sellers = Seller.objects.all()
        return render(request, 'vendor_list.html', {'sellers': sellers})


class SellerDetail(View):
    def get(self, request, pk):
        seller = get_object_or_404(Seller, pk=pk)
        sellergoods = SellerGoods.objects.filter(seller=seller).select_related('goods')
        for sellergood in sellergoods:
            sellergood.total_price = sellergood.quantity * sellergood.goods.price

            context = {
            'seller': seller,
            'sellergoods': sellergoods,

        }

        return render(request, 'seller_detail.html', context)



class PlayerStats(View):
    def get(self, request):
        user_balance = Balance.objects.first()
        user = {'name': user_balance.user.username, 'balance': user_balance.amount}
        return render(request, 'player_stats.html', {'user': user})

class GoodDetail(View):
    def get(self, request, pk):
        good = get_object_or_404(Goods, pk=pk)
        plot_image_base64 = generate_simulation_graph(good.id)

        context = {
            'good': good,
            'plot_image_base64': plot_image_base64,
        }

        return render(request, 'good_detail.html', context)


class BuyGood(View):
    def post(self, request, sellergood_id):
        sellergood = get_object_or_404(SellerGoods, id=sellergood_id)
        buyer_balance = Balance.objects.get(user=request.user)

        if buyer_balance.amount >= sellergood.goods.price and sellergood.quantity > 0:
            total_price = sellergood.goods.price
            buyer_balance.amount -= total_price
            buyer_balance.save()

            transaction = Transaction.objects.create(
                user=request.user,
                seller=sellergood.seller,
                goods=sellergood.goods,
                quantity=1,
                type='buy',
                price=total_price
            )

            # Call the adjust_price_based_on_equilibrium function with transaction_type='buy'
            adjust_price_based_on_equilibrium(sellergood.goods, transaction_type='buy')

            sellergood.quantity -= 1
            sellergood.save()

            if sellergood.quantity == 0:
                sellergood.delete()

            return redirect(reverse('seller_detail', kwargs={'pk': sellergood.seller.pk}))
        else:
            return redirect(reverse('seller_detail', kwargs={'pk': sellergood.seller.pk}))


class SellGood(View):
    def post(self, request, sellergood_id):
        sellergood = get_object_or_404(SellerGoods, id=sellergood_id)
        buyer_balance = Balance.objects.get(user=request.user)

        if sellergood.quantity > 0:

            total_price = sellergood.goods.price
            buyer_balance.amount += total_price
            buyer_balance.save()
            transaction = Transaction.objects.create(
                user=request.user,
                seller=sellergood.seller,
                goods=sellergood.goods,
                quantity=1,
                type='sell',
                price=total_price
            )

            # Call the adjust_price_based_on_equilibrium function with transaction_type='sell'
            adjust_price_based_on_equilibrium(sellergood.goods, transaction_type='sell')

            sellergood.quantity += 1
            sellergood.save()
            if sellergood.quantity == 0:
                sellergood.delete()

            return redirect(reverse('seller_detail', kwargs={'pk': sellergood.seller.pk}))

        return redirect(reverse('seller_detail', kwargs={'pk': sellergood.seller.pk}))





