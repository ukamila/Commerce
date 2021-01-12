from django.contrib import admin

from .models import NewListing, User, Comment, Bid

# Register your models here.
class NewListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "bid", "category", "active")

admin.site.register(User)
admin.site.register(NewListing, NewListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
