from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from SimGame.models import Goods, Seller, SellerGoods


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)




class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise ValidationError('hasła nie są takie same')
        return cleaned_data


class ChooseUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())


class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name']

class GoodsForm(forms.ModelForm):
    class Meta:
        model = Goods
        fields = ['name']

class SellerGoodsForm(forms.ModelForm):
    model = SellerGoods
    fields = ['quantity']


    class Meta:
        model = Goods
        fields = []  # This form doesn't map to any model fields
