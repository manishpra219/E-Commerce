from django.db import models

class Product(models.Model):
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to='shop/images', default="")

    def __str__(self):
        return self.product_name

class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.name

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.TextField()
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=111)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    #razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)  #not need already work
    paid = models.BooleanField(default=False)



class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    # order_id = models.IntegerField(default=0)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True, blank=True)

    update_desc = models.CharField(max_length=5000)
  
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[:7] + "..."
