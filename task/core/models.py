from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name



class Order(models.Model):
    order_id = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_instruction = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

    def save(self, *args, **kwargs):
        """Calculate total price before saving the order."""
        self.total_price = self.quantity * self.item.price
        super().save(*args, **kwargs)
        
        
        
        