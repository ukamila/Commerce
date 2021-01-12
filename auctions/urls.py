from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category_listings, name="category_listings"),
    path("change_watchlist/<str:listing_id>", views.change_watchlist, name="change_watchlist"),
    path("listing/<str:listing>", views.listing, name="listing"),
    path("comment/<str:list_id>", views.comment, name="comment"),
    path("close_auctions/<str:list_id>", views.close_auction, name="close_auction"),
    path("listing/<str:list_id>/place_a_bid", views.place_a_bid, name="place_a_bid"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
