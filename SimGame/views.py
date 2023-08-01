from django.contrib.auth import authenticate, login, logout
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from SimGame.forms import LoginForm, RegisterForm
from SimGame.models import User, UserBalance, SellerGoods, Seller



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
        user_balance = UserBalance.objects.create(user=user, balance=balance)

        return redirect('home')



class PlayerDetail(View):
    def get(self, request, pk):
        user = User.objects.all()
        return render(request, 'player_detail.html')


class PlayerList(View):
    def get(self, request):
        user_balances = UserBalance.objects.all()
        players_data = [{'name': balance.user.name, 'balance': balance.balance} for balance in user_balances]
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

        user_balance = UserBalance.objects.first()
        user = {'name': user_balance.user.name, 'balance': user_balance.balance}
        return render(request, 'player_stats.html', {'user': user})

