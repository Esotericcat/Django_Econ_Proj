from django.db import models

class User(models.Model):
    name = models.CharField(max_length=64)


class UserBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)


class Goods(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Seller(models.Model):
    name = models.CharField(max_length=64)


class SellerGoods(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    type = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)






