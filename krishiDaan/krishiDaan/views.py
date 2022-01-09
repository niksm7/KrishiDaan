from django.shortcuts import render, reverse

from toolz.functoolz import apply
from .utils import web, operations_contract, upload_to_ipfs, token_address
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
import pyrebase
from django.contrib import auth
import os
import json
import bisect
from apscheduler.schedulers.background import BackgroundScheduler
from krishiapp.models import WebUser
from django.contrib.auth import models
from django.core.files.storage import default_storage

config = {
    "apiKey": "",
    "authDomain": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
storage = firebase.storage()

scheduler = BackgroundScheduler()
scheduler.start()

available_goods = []

def login_page(request):
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        if user.group.name == "Farmer":
            return HttpResponseRedirect(reverse("requestGoods"))
        else:
            return HttpResponseRedirect(reverse("shop"))
    return render(request, 'login.html')


def home(request):
    return render(request, 'home.html')

def shop(request):
    return render(request, 'donor/shop.html')


def requestGoods(request):
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        if user.group.name == "Farmer": 
            return render(request, 'farmer/request-goods.html')
    return HttpResponse('Unauthorized', status=401)


def profile(request):
    if request.session.get('uid') is not None:
        return render(request, 'profile.html')
    return HttpResponse('Unauthorized', status=401)


def allocatedGoods(request):
    if request.session.get('uid') is not None:
        user = WebUser.objects.filter(id=request.session['uid'])[0]
        if user.group.name == "Farmer":
            return render(request, 'farmer/allocated-goods.html', {"farmer_address": json.dumps(user.account_address)})
    return HttpResponse('Unauthorized', status=401)


def adminHome(request):
    if request.user.is_superuser:
        return render(request, 'admin-home.html')
    return HttpResponse('Unauthorized', status=401)


def addGoods(request):
    if request.user.is_superuser:
        if request.method == "POST":
            name = request.POST.get("good_name")
            token_amount = int((float(request.POST.get("good_price")))*(10**18))
            image = request.FILES.get("good_image")
            description = request.POST.get("good_desc")

            image_uri = upload_to_ipfs(image)

            nonce = web.eth.get_transaction_count(web.toChecksumAddress(web.eth.default_account))
            operation_tx = operations_contract.functions.addGoods(name, token_amount, image_uri, description).buildTransaction({
                'chainId': 4,
                'gas': 7000000,
                'gasPrice': web.toHex((10**11)),
                'nonce': nonce,
                })
            signed_tx = web.eth.account.sign_transaction(operation_tx, private_key=os.getenv("PRIVATE_KEY"))
            receipt = web.eth.send_raw_transaction(signed_tx.rawTransaction)
            web.eth.wait_for_transaction_receipt(receipt)
            print("Good will be added soon!")

        return render(request, "addItem.html")
    return HttpResponse('Unauthorized', status=401)


def placeRequestGoods(request):
    user = WebUser.objects.filter(id=request.session['uid'])[0]
    farmer_address = user.account_address
    good_ids = json.loads(request.GET.get("good_ids"))
    nonce = web.eth.get_transaction_count(web.toChecksumAddress(web.eth.default_account))
    operation_tx = operations_contract.functions.requestDonation(farmer_address, good_ids).buildTransaction({
        'chainId': 4,
        'gas': 7000000,
        'gasPrice': web.toHex((10**11)),
        'nonce': nonce,
        })
    signed_tx = web.eth.account.sign_transaction(operation_tx, private_key=os.getenv("PRIVATE_KEY"))
    receipt = web.eth.send_raw_transaction(signed_tx.rawTransaction)
    web.eth.wait_for_transaction_receipt(receipt)
    return JsonResponse({"sucess": "ok"})


def donatedGoods(request):
    good_ids = json.loads(request.GET.get("good_ids"))
    available_goods.extend(good_ids)
    return JsonResponse({"sucess": "ok"})


def donatedCoins(request):
    available_coins = operations_contract.functions.available_coins().call()
    total_amount_coins = int(json.loads(request.GET.get("total_amount_coins"))) + available_coins
    all_goods = operations_contract.functions.getAllGoods().call()
    waiting_lists = []
    good_to_waiting = {}
    good_to_amount = {}
    goods_to_availability = {}
    good_ids = []
    good_qts = []
    for good in all_goods:
        val = operations_contract.functions.goods_to_waiting(good[0]).call()
        waiting_lists.insert(bisect.bisect(waiting_lists, val), good[0])
        good_to_waiting[good[0]] = val
        good_to_amount[good[0]] = good[2]
        goods_to_availability[good[0]] = operations_contract.functions.goods_to_availability(good[0]).call()

    for item in range(len(waiting_lists)-1, -1, -1):
        if total_amount_coins != 0:
            qty = 0

            if item != 0 and goods_to_availability[waiting_lists[item]] > (goods_to_availability[waiting_lists[item-1]]+1)*2:
                continue

            if good_to_amount[waiting_lists[item]] < total_amount_coins:
                good_ids.append(waiting_lists[item])

            while good_to_amount[waiting_lists[item]] < total_amount_coins:
                if item != 0 and goods_to_availability[waiting_lists[item]] > (goods_to_availability[waiting_lists[item-1]]+1)*2:
                    break
                qty += 1
                goods_to_availability[waiting_lists[item]] += 1
                total_amount_coins -= good_to_amount[waiting_lists[item]]
            if qty != 0:
                good_qts.append(qty)
        else:
            break

    available_goods.extend(good_ids)

    nonce = web.eth.get_transaction_count(web.toChecksumAddress(web.eth.default_account))
    operation_tx = operations_contract.functions.increaseGoodQuantity(good_ids, good_qts, total_amount_coins).buildTransaction({
        'chainId': 4,
        'gas': 7000000,
        'gasPrice': web.toHex((10**11)),
        'nonce': nonce,
        })
    signed_tx = web.eth.account.sign_transaction(operation_tx, private_key=os.getenv("PRIVATE_KEY"))
    receipt = web.eth.send_raw_transaction(signed_tx.rawTransaction)
    web.eth.wait_for_transaction_receipt(receipt)

    return JsonResponse({"Success": "OK"})


def distributeGoods():
    print(available_goods)
    nonce = web.eth.get_transaction_count(web.toChecksumAddress(web.eth.default_account))
    operation_tx = operations_contract.functions.distributeDonation(available_goods).buildTransaction({
        'chainId': 4,
        'gas': 7000000,
        'gasPrice': web.toHex((10**11)),
        'nonce': nonce,
        })
    signed_tx = web.eth.account.sign_transaction(operation_tx, private_key=os.getenv("PRIVATE_KEY"))
    receipt = web.eth.send_raw_transaction(signed_tx.rawTransaction)
    web.eth.wait_for_transaction_receipt(receipt)


scheduler.add_job(distributeGoods, 'cron', hour=2)


def distribute(request):
    distributeGoods()
    return render(request, "admin-home.html")


# Authentication

def handleLogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = authe.sign_in_with_email_and_password(email, password)
            if authe.get_account_info(user['idToken'])['users'][0]["emailVerified"] is False:
                try:
                    authe.send_email_verification(user['idToken'])
                    message = "Please verify the email! Link has been sent!"
                except Exception:
                    message = "Please verify the email! Link has been sent!"
                return render(request, 'login.html', {"msg": message})

        except Exception:
            message = "Invalid Credentials"
            return render(request, 'login.html', {"msg": message})

        session_id = user['localId']
        request.session['email'] = email
        request.session['usrname'] = email.split("@")[0]
        request.session['uid'] = str(session_id)
    return HttpResponseRedirect(reverse("login_page"))


def handleSignUpUser(request):
    if request.method == "POST":
        email = request.POST.get("email")
        full_name = request.POST.get("fullname")
        password = request.POST.get("password")
        new_user = authe.create_user_with_email_and_password(email, password)
        web_user = WebUser(id=new_user["localId"], full_name=full_name, group=models.Group.objects.filter(name="NormalUser")[0])
        web_user.save()
    return HttpResponseRedirect(reverse("home"))


def handleSignUpFarmer(request):
    if request.method == "POST":
        email = request.POST.get("email")
        full_name = request.POST.get("fullname")
        password = request.POST.get("password")
        farmer_id = request.POST.get("farmerid")
        aadhaar_card = request.FILES.get("aadhaarcard")
        account_address = request.POST.get("accadd")

        new_user = authe.create_user_with_email_and_password(email, password)

        file_name = new_user["localId"] + "_aadhaar" + ".pdf"

        default_storage.save(file_name, aadhaar_card)
        storage.child("aadhaars/" + file_name).put("media/" + file_name)
        default_storage.delete(file_name)

        web_user = WebUser(
            id=new_user["localId"], 
            full_name=full_name,
            farmer_id=farmer_id,
            aadhaar_link="https://firebasestorage.googleapis.com/v0/b/.appspot.com/o/aadhaars%2F{}_aadhaar.pdf?alt=media".format(new_user["localId"]),
            request_farmer=True,
            account_address=account_address,
            group=models.Group.objects.filter(name="NormalUser")[0])

        web_user.save()

    return HttpResponseRedirect(reverse("home"))


def handleLogout(request):
    if request.session.get('uid') is not None:
        auth.logout(request)
        authe.current_user = None
    return HttpResponseRedirect(reverse("home"))