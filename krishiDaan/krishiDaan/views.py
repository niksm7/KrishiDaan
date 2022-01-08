from django.shortcuts import render, reverse
from .utils import web, operations_contract, upload_to_ipfs, token_address
from django.http import HttpResponseRedirect, JsonResponse
import pyrebase
from django.contrib import auth


def loginpage(request):
    return render(request, 'login.html')


def shop(request):
    return render(request, 'donor/shop.html')


def requestGoods(request):
    return render(request, 'farmer/request-goods.html')


def profile(request):
    return render(request, 'profile.html')


def pendingRequest(request):
    return render(request, 'farmer/pending-req.html')


def donations(request):
  return render(request,'donations.html') 