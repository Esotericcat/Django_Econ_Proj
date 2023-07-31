from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View

from SimGame.forms import LoginForm, RegisterForm
from SimGame.models import User, UserBalance


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