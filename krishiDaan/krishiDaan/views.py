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


scheduler = BackgroundScheduler()
scheduler.start()

available_goods = []


def loginpage(request):
    return render(request, 'login.html')


def shop(request):
    return render(request, 'donor/shop.html')


def requestGoods(request):
    return render(request, 'farmer/request-goods.html')


def profile(request):
    return render(request, 'profile.html')



def allocatedGoods(request):
    return render(request, 'farmer/allocated-goods.html')


def adminHome(request):
    return render(request, 'admin-home.html')



def addGoods(request):
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


def placeRequestGoods(request):
    # Get farmer address by login info
    farmer_address = "0xD559520fBC54D0f7813C045A40db703cD3F55D1e"
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
    print("herere")
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