from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("NewListing", blank=True, related_name="watchlist")

class NewListing(models.Model):
    ACTIVE_CATEGORIES = [
        ('MOTORS', 'Motors'),
        ('FASHION', 'Fashion'),
        ('BOOKS', 'Books'),
        ('MOVIES', 'Movies'),
        ('MUSIC', 'Music'),
        ('ELECTRONICS', 'Electronics'),
        ('COLLECTIBLES', 'Collectibles'),
        ('ART', 'Art'),
        ('HOME', 'Home'),
        ('GARDEN', 'Garden'),
        ('SPORTING GOODS', 'Sporting Goods'),
        ('TOYS', 'Toys'),
        ('HOBBIES', 'Hobbies'),
        ('BUSINESS', 'Business'),
        ('INDUSTRIAL', 'Industrial'),
        ('HEALTH', 'Health'),
        ('BEAUTY', 'Beauty'),
        ('ANIMALS', 'Animals'),
        ('FAMILY', 'Family'),
        ('NONE', 'None')
    ]
    title = models.CharField(max_length=64)
    seller =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="Owner")
    description = models.CharField(max_length=600)
    bid = models.IntegerField()  
    category = models.CharField(choices=ACTIVE_CATEGORIES, blank=True, verbose_name="Category", max_length=200, null=True)
    active = models.BooleanField(default=True)
    image = models.URLField(max_length = 250, null=True)
    datetime = models.DateTimeField(auto_now_add=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="Winner", blank=True)
    
    def __str__(self):
        return f"{self.title}"       

class Bid(models.Model):
    buyer =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="Buyer")
    listing = models.ForeignKey(NewListing, on_delete=models.CASCADE, related_name="Bid")
    highest_bid = models.IntegerField(null=True)

class Comment(models.Model): 
    user =  models.ForeignKey(User, on_delete=models.CASCADE, related_name="Comment_User")
    text = models.TextField(max_length=150)
    listing = models.ForeignKey(NewListing, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, null=True)

