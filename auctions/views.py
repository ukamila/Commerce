from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime, timezone
import pytz
from django.contrib.auth.decorators import login_required

from .models import User, NewListing, Comment, Bid


def index(request):
    return render(request, "auctions/index.html", {
        "listings": NewListing.objects.filter(active=True).order_by("title"),
        "is_category": False
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return render(request, "auctions/index.html", {
                "listings": NewListing.objects.filter(active=True).order_by("title")
            })
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    categories = NewListing.objects.order_by("category").values_list("category", flat=True).distinct()
    if request.method == "POST":
        title = request.POST['t']
        description = request.POST['d']
        starting_bid = request.POST['b']
        other = request.POST['c2']
        if len(other)<1:
            category = request.POST['c1']
        else:
            category = request.POST['c2']
        category = category.upper()
        date = datetime.utcnow().replace(tzinfo=pytz.utc)
        user = request.user
        image = request.POST['i']
        newListing = NewListing(title=title, seller=user, description=description, bid=starting_bid, category=category, image=image, datetime=date)
        newListing.save()
        newBid = Bid(buyer=user, listing=newListing, highest_bid=starting_bid)
        newBid.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create.html", {
        "categories": categories,
    })

def is_in_watchlist(request, listing):
    if request.user.is_authenticated:
        in_watchlist = listing in request.user.watchlist.all()
    else:
        in_watchlist = False
    return in_watchlist

@login_required
def change_watchlist(request, listing_id):
    listing = NewListing.objects.get(pk=listing_id)
    in_watchlist = is_in_watchlist(request, listing)
    if in_watchlist:
        request.user.watchlist.remove(listing_id)
    else:
        request.user.watchlist.add(listing_id)
    return HttpResponseRedirect(reverse("listing", args=(listing,)))

def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all(),
    })

def listing(request, listing):
    listing = NewListing.objects.get(title=listing)
    allBids = Bid.objects.filter(listing=listing)
    number = len(allBids)
    current_user = request.user
    highest_bid = Bid.objects.filter(listing=listing).order_by('-id')[0]
    highest_bidder = highest_bid.buyer
    watchlist = is_in_watchlist(request, listing)
    all_comments = Comment.objects.filter(listing=listing).order_by("-created_on")
    if current_user.username == highest_bidder.username:
        your_bid = True
    else:
        your_bid = False
    return render(request, "auctions/listing.html", {
        "list": listing,
        "num_bids": number,
        "your_bid": your_bid,
        "in_watchlist": watchlist,
        "all_comments": all_comments
    })

@login_required
def place_a_bid(request, list_id):
    if request.method == "POST":
        user = request.user
        listing1 = NewListing.objects.get(pk=list_id)
        amount = request.POST['new_bid']
        if Bid.objects.filter(listing=listing1).order_by('-id')[0].highest_bid > int(amount):
            return HttpResponse("Error: Your bid should be higher than the current bid. Please return to a previous page.")
        if len(Bid.objects.filter(listing=listing1).filter(buyer=user))>0 :
            Bid.objects.filter(listing=listing1).filter(buyer=user).delete()
            updateBid = Bid(buyer=user, listing=listing1, highest_bid=amount)
            updateBid.save()
            listing1.bid = amount
            listing1.save()
        else:
            newBid = Bid(buyer=user, listing=listing1, highest_bid=amount)
            newBid.save()
            listing1.bid = amount
            listing1.save()
        allBids = Bid.objects.filter(listing=listing1)
        number = len(allBids)
        current_user = request.user
        highest_bid = Bid.objects.filter(listing=listing1).order_by('-id')[0]
        highest_bidder = highest_bid.buyer
        watchlist = is_in_watchlist(request, listing1)
        all_comments = Comment.objects.filter(listing=listing1).order_by("-created_on")
        if current_user.username == highest_bidder.username:
            your_bid = True
        else:
            your_bid = False
        return render(request, "auctions/listing.html", {
            "list": listing1,
            "num_bids": number,
            "your_bid": your_bid,
            "in_watchlist": watchlist,
            "all_comments": all_comments
        })

def categories(request):
    categories = NewListing.objects.order_by("category").values_list("category", flat=True).distinct()
    categories = [category.capitalize() for category in categories if category is not None]
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_listings(request, category):
    return render(request, "auctions/index.html", {
        "listings": NewListing.objects.filter(active=True).filter(category=category.upper()).order_by("title"),
        "is_category": True
    })

@login_required
def comment(request, list_id):
    listing1 = NewListing.objects.get(pk=list_id)
    watchlist = is_in_watchlist(request, listing1)
    if request.method == "POST":
        user = request.user
        comment = request.POST['new_comment']
        date = datetime.now().astimezone()
        newComment = Comment(user=user, listing=listing1, text=comment, created_on=date)
        newComment.save()
        return HttpResponseRedirect(reverse("listing", args=(listing1.title,)))
    allBids = Bid.objects.filter(listing=listing1)
    number = len(allBids)
    all_comments = Comment.objects.filter(listing=listing1).order_by("-created_on")
    return render(request, "auctions/listing.html", {
        "list": NewListing.objects.get(pk=list_id),
        "num_bids": number,
        "your_bid": True,
        "all_comments": all_comments,
        "in_watchlist": watchlist
    })

@login_required
def close_auction(request, list_id):
    listing1 = NewListing.objects.get(pk=list_id)
    highest_bid = Bid.objects.filter(listing=listing1).order_by("highest_bid").last()
    if highest_bid:
        listing1.winner = highest_bid.buyer
    listing1.active = False
    listing1.save()

    return HttpResponseRedirect(reverse("listing", args=(listing1,)))
