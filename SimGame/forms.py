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
    class Meta:
        model = SellerGoods
        fields = ['seller', 'goods', 'quantity']


class AddGoodsForm(forms.Form):
    goods = forms.ModelChoiceField(queryset=Goods.objects.all(), empty_label="Select a goods")
    quantity = forms.IntegerField(min_value=1)


class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name']



class CreateSellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name']




class ChangePriceOrCreateGoodForm(forms.Form):
    good = forms.ModelChoiceField(queryset=Goods.objects.all(), empty_label="Select a good or create a new one", required=False)
    new_good_name = forms.CharField(max_length=64, required=False)
    price = forms.DecimalField(max_digits=10, decimal_places=2)