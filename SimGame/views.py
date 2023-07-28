from django.shortcuts import render
from django.views import View

from SimGame.forms import LoginForm


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'form.html', {'form': form})
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            return render(request, 'home.html', {'form': form})
        else:
            return render(request, 'form.html', {'form': form})



class Home(View):
    def get(self, request):
        return render(request, 'home.html')



# Create your views here.
