from django.shortcuts import render, redirect
import pyrebase
from django.contrib import auth


def loginpage(request):
  return render(request,'login.html') 

def shop(request):
  return render(request,'shop.html') 
