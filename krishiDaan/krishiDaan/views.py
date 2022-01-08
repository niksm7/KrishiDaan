from django.shortcuts import render, redirect


def loginpage(request):
  return render(request,'login.html') 

def shop(request):
  return render(request,'shop.html') 

def requestGoods(request):
  return render(request,'request-goods.html') 

def donorProfile(request):
  return render(request,'donor-profile.html') 

def pendingRequest(request):
  return render(request,'pending-req.html') 

def donations(request):
  return render(request,'donations.html') 