from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=64)
    money = models.IntegerField(default=500)
    def __str__(self):
        return self.name
class Good(models.Model):
    name = models.CharField(max_length=64)
    price = models.IntegerField(default=0)
    def __str__(self):
        return self.name


class Transaction(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    good = models.ForeignKey(Good, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    transaction_type = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.player.name} {self.good.name} {self.quantity}'


# Create your models here.
