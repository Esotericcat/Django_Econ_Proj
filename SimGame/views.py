from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from SimGame.forms import LoginForm, RegisterForm, ChooseUserForm
from SimGame.models import Balance, SellerGoods, Seller, Transaction, Inventory


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






class PlayerCreate(View):
    def get(self, request):
        return render(request, 'player_create.html')
    def post(self, request):
        name = request.POST.get('name')
        balance = request.POST.get('balance')
        user = User.objects.create(name=name)
        user_balance = Balance.objects.create(user=user, balance=balance)

        return redirect('home')



class PlayerDetail(View):
    def get(self, request, pk):
        user =  User.objects.all()
        return render(request, 'player_detail.html')


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

        return render(request, 'seller_detail.html', {'seller': seller, 'sellergoods': sellergoods})



class PlayerStats(View):
    def get(self, request):
        user_balance = Balance.objects.first()
        user = {'name': user_balance.user.username, 'balance': user_balance.amount}
        return render(request, 'player_stats.html', {'user': user})



class BuyGood(View):
    def post(self, request, sellergood_id):
        sellergood = get_object_or_404(SellerGoods, id=sellergood_id)
        buyer_balance = Balance.objects.get(user=request.user)
        if buyer_balance.amount >= sellergood.goods.price and sellergood.quantity > 0:
            # Calculate the total price of one item
            total_price = sellergood.goods.price

            # Deduct the purchase price from the buyer's balance
            buyer_balance.amount -= total_price
            buyer_balance.save()

            # Record the transaction
            transaction = Transaction.objects.create(
                user=request.user,
                seller=sellergood.seller,
                goods=sellergood.goods,
                quantity=1,  # Buy only one item at a time
                type='buy',
                price=total_price
            )

            # Create or update the Inventory for the user
            inventory_item, created = Inventory.objects.get_or_create(
                user=request.user,
                goods=sellergood.goods,
            )
            inventory_item.quantity += 1
            inventory_item.save()

            # Decrease the quantity of the SellerGood by one
            sellergood.quantity -= 1
            sellergood.save()

            # If the quantity is zero, remove the SellerGood from the seller's list
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
                quantity=1,  # Buy only one item at a time
                type='sell',
                price=total_price
            )

            # Create or update the Inventory for the user
            inventory_item, created = Inventory.objects.get_or_create(
                user=request.user,
                goods=sellergood.goods,
            )
            inventory_item.quantity -= 1
            inventory_item.save()

            # Decrease the quantity of the SellerGood by one
            sellergood.quantity += 1
            sellergood.save()

            # If the quantity is zero, remove the SellerGood from the seller's list
            if sellergood.quantity == 0:
                sellergood.delete()

            return redirect(reverse('seller_detail', kwargs={'pk': sellergood.seller.pk}))


        return redirect(reverse('seller_detail', kwargs={'pk': sellergood.seller.pk}))