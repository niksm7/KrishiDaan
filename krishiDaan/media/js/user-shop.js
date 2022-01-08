const web = new Web3("https://rinkeby.infura.io/v3/")
var token_contract = ""
var operations_contract = ""
var current_user_account = ""
var good_ids = ""
const address_coin = ""
const address_operations = ""

$.ajax({
    url: "https://api-rinkeby.etherscan.io/api?module=contract&action=getabi&address=&apikey=",
    dataType: "json",
    success: function (data) {
        token_contract = new web.eth.Contract(JSON.parse(data.result), address_coin)
        localStorage.setItem('token_contract', JSON.stringify([JSON.parse(data.result), address_coin]))
    }
});

$.ajax({
    url: "https://api-rinkeby.etherscan.io/api?module=contract&action=getabi&address=&apikey=",
    dataType: "json",
    success: function (data) {
        operations_contract = new web.eth.Contract(JSON.parse(data.result), address_operations)
        localStorage.setItem('operations_contract', JSON.stringify([JSON.parse(data.result), address_operations]))
        display_goods()
    }
});

window.addEventListener('load', async () => {

    if (window.ethereum) {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            current_user_account = accounts[0]
        } catch (error) {
            if (error.code === 4001) {
                // User rejected request
            }

            setError(error);
        }
        window.ethereum.on('accountsChanged', (accounts) => {
            current_user_account = accounts[0]
        });

    } else {
        window.alert(
            "Non-Ethereum browser detected. You should consider trying MetaMask!"
        );
    }
})


function donationBackend(hash, all_good_ids){
    $("#loader_text").text("Donating")
    web.eth.getTransactionReceipt(hash, async function (err, receipt) {
        if (err) {
            console.log(err)
        }

        if (receipt !== null) {
            try {
                good_ids = JSON.parse(all_good_ids)
                $.ajax({
                    url: "/donatedgoods/",
                    dataType: "json",
                    data:{
                        "good_ids": all_good_ids
                    },
                    success: function (data) {
                        document.getElementById("loader_container").hidden = true
                        document.getElementById("main_container").hidden = false
                    }
                });
            } catch (e) {
                console.log(e)
            }
        } else {
            // Try again in 1 second
            window.setTimeout(function () {
                donationBackend(hash, all_good_ids);
            }, 1000);
        }
    });
}


function payForOrder(hash, all_good_ids, all_good_qtys) {
    document.getElementById("loader_container").hidden = false
    document.getElementById("main_container").hidden = true
    $("#loader_text").text("Approving")
    web.eth.getTransactionReceipt(hash, async function (err, receipt) {
        if (err) {
            console.log(err)
        }

        if (receipt !== null) {
            try {
                good_ids = JSON.parse(all_good_ids)
                good_qtys = JSON.parse(all_good_qtys)
                transaction2 = operations_contract.methods.placeDonation(address_coin, current_user_account, good_ids, good_qtys, all_good_ids, all_good_qtys)
                tx2 = await send(transaction2)
                donationBackend(tx2,all_good_ids)
            } catch (e) {
                console.log(e)
            }
        } else {
            // Try again in 1 second
            window.setTimeout(function () {
                payForOrder(hash, all_good_ids, all_good_qtys);
            }, 1000);
        }
    });
}


async function send(transaction, value = 0) {
    const params = [{
        from: current_user_account,
        to: transaction._parent._address,
        data: transaction.encodeABI(),
        gas: web.utils.toHex(1000000),
        gasPrice: web.utils.toHex(10e10),
        value: web.utils.toHex(value)
    },]

    sending_tx = window.ethereum.request({
        method: 'eth_sendTransaction',
        params,
    })

    await sending_tx;
    return await sending_tx
}


async function place_donation(){
    // Calculate total amount of cart
    cart = JSON.parse(localStorage.getItem('shoppingCart'))
    var good_ids = []
    var good_qtys = []
    for(var item in cart){
        good_ids.push(cart[item]["good_id"])
        good_qtys.push(cart[item]["count"])
    }
    confirmed_total = 0
    let promises = [];
    for (let good_index = 0; good_index < good_ids.length; good_index++) {
        amount = operations_contract.methods.id_to_good(good_ids[good_index]).call()
        promises.push(amount)
        amount = JSON.parse(JSON.stringify(await amount))["token_amount"]
        confirmed_total = confirmed_total + (await amount * good_qtys[good_index])
    }
    const results = await Promise.all(promises);
    confirmed_total = await confirmed_total.toString()
    transaction1 = token_contract.methods.approve(address_operations, confirmed_total)
    tx = await send(transaction1)
    payForOrder(tx.toString(), JSON.stringify(good_ids), JSON.stringify(good_qtys))
}

async function display_goods() {
    var all_goods = await operations_contract.methods.getAllGoods().call();
    for(var good in all_goods){
        $("#goods_row").append(`
        <div class="col">
            <div class="card" style="width: 20rem;">
                <img class="card-img-top" src="${all_goods[good]["image_uri"]}"
                    alt="Card image cap">
                <div class="card-block">
                    <h4 class="card-title">${all_goods[good]["name"]}</h4>
                    <p class="card-text">Price: ${all_goods[good]["token_amount"] / (10**18)}</p>
                    <a href="#" data-name="${all_goods[good]["name"]}" data-goodid="${all_goods[good]["id"]}" data-price="${all_goods[good]["token_amount"]}" class="add-to-cart btn btn-primary">Add to
                        cart</a>
                </div>
            </div>
        </div>
        `)
    }
    $('.add-to-cart').click(function(event) {
        event.preventDefault();
        var name = $(this).data('name');
        var price = Number($(this).data('price'));
        var good_id = Number($(this).data('goodid'))
        shoppingCart.addItemToCart(name, price, 1, good_id);
        displayCart();
    });
}