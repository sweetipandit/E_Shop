from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class TshirtProperty(models.Model):
    title = models.CharField(max_length=30, null=False, default="")
    slug = models.CharField(max_length=30, null=False, default="")

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class Occasion(TshirtProperty):
    pass


class IdealFor(TshirtProperty):
    pass


class NeckType(TshirtProperty):
    pass


class Sleeve(TshirtProperty):
    pass


class Brand(TshirtProperty):
    pass


class Color(TshirtProperty):
    pass



class Tshirt(models.Model):
    name = models.CharField(max_length=50, null=False)
    slug = models.CharField(max_length=200, null=False ,unique=True)
    description = models.CharField(max_length=500, null=True)
    descount = models.IntegerField(default=0)
    image = models.ImageField(upload_to='upload/images/', null=False)
    occasion = models.ForeignKey(Occasion, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    sleeve = models.ForeignKey(Sleeve, on_delete=models.CASCADE)
    neck_type = models.ForeignKey(NeckType, on_delete=models.CASCADE)
    ideal_for = models.ForeignKey(IdealFor, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class SizeVariant(models.Model):
    SIZES =(
        ('S', "small"),
        ('M', "mediam"),
        ('L', "large"),
        ('XL', "Extra Large"),
        ('XXL', "Ex Ex Large"),

    )
    tshirt = models.ForeignKey(Tshirt ,on_delete=models.CASCADE)
    prize = models.IntegerField(null=False)
    size = models.CharField(choices=SIZES, max_length=6)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sizeVariant = models.ForeignKey(SizeVariant ,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class Order(models.Model):
    ORDER_STATUS={
        ('PENDING' , "Pending"),
        ('PLACED', "Placed"),
        ('CANCELED', "Canceled"),
        ('COMPLETED', "Completed"),
    }
    METHODS = {
        ('COD', "Cod"),
        ('ONLINE', "Online"),

    }

    order_status = models.CharField(choices=ORDER_STATUS, max_length=15)
    payment_method = models.CharField(choices=METHODS, max_length=15)
    shipping_address = models.CharField(null=False, max_length=100)
    phone = models.CharField(null=False, max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.IntegerField(null=False)
    date = models.DateTimeField(null=False,auto_now_add=True)

    def __str__(self):
        return f'{self.user}------{self.order_status}-------{self.shipping_address}-----{self.phone}----{self.total}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    tshirt = models.ForeignKey(Tshirt, on_delete=models.CASCADE)
    sizeVariant = models.ForeignKey(SizeVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False)
    price=models.IntegerField(null=False)
    date = models.DateTimeField(null=False,auto_now_add=True)
    def __str__(self):
        return f'{self.order.user}------{self.tshirt.name}-------{self.sizeVariant.size}-----{self.price}-----{self.quantity}'


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False,auto_now_add=True)
    payment_status = models.CharField(max_length=15, default="FAILED")
    payment_id = models.CharField(max_length=60)
    payment_request_id = models.CharField(max_length=60, null=False, unique=True)
    def __str__(self):
        return f'{self.order.user}------{self.payment_status}-------{self.payment_id}-----{self.payment_request_id}'




