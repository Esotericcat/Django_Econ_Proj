from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


@receiver(post_save, sender=User)
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        Balance.objects.create(user=instance, amount=0.00)

@receiver(post_save, sender=User)
def save_user_balance(sender, instance, **kwargs):
    instance.balance.save()


class Goods(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cumulative_demand = models.IntegerField(default=0)

    def __str__(self):
        return self.name






class Seller(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class SellerGoods(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return self.name



class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    type = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    cumulative_quantity_sum = models.IntegerField(default=0)


    demand_change = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super(Transaction, self).save(*args, **kwargs)

        if self.type == 'buy':
            self.cumulative_quantity_sum += self.quantity
        elif self.type == 'sell':
            self.cumulative_quantity_sum -= self.quantity

        if self.type == 'buy':
            self.demand_change = self.quantity
        elif self.type == 'sell':
            self.demand_change = -self.quantity

        self.goods.cumulative_demand += self.demand_change
        self.goods.save()

    @property
    def cumulative_demand(self):
        return self.goods.cumulative_demand
class Inventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s {self.goods.name} - Quantity: {self.quantity}"

class Demand(models.Model):
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    demand = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.goods.name} - Demand: {self.demand}"