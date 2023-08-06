import decimal

from django.contrib.auth import authenticate, login, logout
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
    # Calculate total quantity bought and sold for the good
    total_quantity_sold = Transaction.objects.filter(goods=good, type='sell').aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_quantity_bought = Transaction.objects.filter(goods=good, type='buy').aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Calculate demand based on total quantities
    demand = total_quantity_bought - total_quantity_sold
    return demand

def generate_simulation_graph(good_id):
    transactions = Transaction.objects.filter(goods_id=good_id).order_by('date')

    price_data = [transaction.price for transaction in transactions]
    demand_data = []

    # Calculate demand every 25 transactions
    for i in range(0, len(transactions), 25):
        subset_transactions = transactions[:i + 1]  # Include transactions up to index i

        demand = calculate_demand(transactions[i].goods)
        demand_data.append(demand)

    plt.figure(figsize=(12, 6))

    # Plot Price Graph
    plt.subplot(2, 1, 1)
    plt.plot(price_data, label='Price')
    plt.xlabel('Number of Transactions')
    plt.ylabel('Price')
    plt.title(f'Price Simulation Over Time for Good {good_id}')
    plt.legend()

    # Plot Demand Graph
    plt.subplot(2, 1, 2)
    plt.plot(demand_data, label='Demand', color='orange')
    plt.xlabel('Number of Transactions')
    plt.ylabel('Demand')
    plt.title(f'Demand Simulation Over Time for Good {good_id}')
    plt.legend()

    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    # Return the base64 encoded image
    buffer.seek(0)
    plot_image_base64 = base64.b64encode(buffer.read()).decode()
    return plot_image_base64
class LoginView(View):
    def get(self, request):
            return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')  # pobranie danych z formularza
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

        # Generate the simulation graph for the specific good
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

            # Increase the price by a certain percentage
            percentage_increase = Decimal('0.05')  # For example, 5% increase
            new_price = total_price + (total_price * percentage_increase)

            # Update the price of the Goods object
            sellergood.goods.price = new_price
            sellergood.goods.save()


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
        invetory = Inventory.objects.get(user=request.user, goods=sellergood.goods)

        if sellergood.quantity > 0:
            # Calculate the total price of one item
            total_price = sellergood.goods.price

            # Deduct the purchase price from the buyer's balance
            buyer_balance.amount += total_price
            buyer_balance.save()

            # Record the transaction
            transaction = Transaction.objects.create(
                user=request.user,
                seller=sellergood.seller,
                goods=sellergood.goods,
                quantity=1,
                type='sell',
                price=total_price
            )



            inventory_item, created = Inventory.objects.get_or_create(
                user=request.user,
                goods=sellergood.goods,
            )
            inventory_item.quantity -= 1
            inventory_item.save()

            percentage_decrease = Decimal('0.05')  # 5% decrease
            new_price = total_price - (total_price * percentage_decrease)

            sellergood.goods.price = new_price
            sellergood.goods.save()



            sellergood.quantity += 1
            sellergood.save()


            if sellergood.quantity == 0:
                sellergood.delete()
            elif inventory_item.quantity < 0:
                return redirect(reverse('seller_detail', kwargs={'pk': sellergood.seller.pk}))


            return redirect(reverse('seller_detail', kwargs={'pk': sellergood.seller.pk}))



        return redirect(reverse('seller_detail', kwargs={'pk': sellergood.seller.pk}))








