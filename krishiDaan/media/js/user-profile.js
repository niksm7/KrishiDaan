const web = new Web3("https://rinkeby.infura.io/v3/")
token_contract_details = JSON.parse(localStorage.getItem("token_contract"))
operations_contract_details = JSON.parse(localStorage.getItem("operations_contract"))
var token_contract = new web.eth.Contract(token_contract_details[0], token_contract_details[1])
var operations_contract = new web.eth.Contract(operations_contract_details[0], operations_contract_details[1])
var current_user_account = ""

window.addEventListener('load', async () => {

    if (window.ethereum) {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            current_user_account = accounts[0]
            $("#curr_user_account").text(current_user_account)
            refresh_account()
        } catch (error) {
            if (error.code === 4001) {
                // User rejected request
            }

            setError(error);
        }
        window.ethereum.on('accountsChanged', (accounts) => {
            current_user_account = accounts[0]
            $("#curr_user_account").text(current_user_account)
            refresh_account()
        });

    } else {
        window.alert(
            "Non-Ethereum browser detected. You should consider trying MetaMask!"
        );
    }
})


function coin_backend(hash, total_amount){
    web.eth.getTransactionReceipt(hash, async function (err, receipt) {
        if (err) {
            console.log(err)
        }

        if (receipt !== null) {
            document.getElementById("loader_container").hidden = true
            document.getElementById("main_container").hidden = false
            try {
                $.ajax({
                    url: "/donatedcoins/",
                    dataType: "json",
                    data:{
                        "total_amount_coins": total_amount
                    },
                    success: function (data) {
                        console.log("success")
                    }
                });
            } catch (e) {
                console.log(e)
            }
        } else {
            // Try again in 1 second
            window.setTimeout(function () {
                coin_backend(hash, total_amount);
            }, 1000);
        }
    });
}


function payOnlyCoins(hash, total_amount) {
    document.getElementById("loader_container").hidden = false
    document.getElementById("main_container").hidden = true
    $("#loader_text").text("Approving")
    web.eth.getTransactionReceipt(hash, async function (err, receipt) {
        if (err) {
            console.log(err)
        }

        if (receipt !== null) {
            try {
                $("#loader_text").text("Donating")
                transaction2 = operations_contract.methods.donateCoins(token_contract_details[1], current_user_account, total_amount.toString(), 0)
                tx2 = await send(transaction2)
                coin_backend(hash, total_amount)
            } catch (e) {
                console.log(e)
            }
        } else {
            // Try again in 1 second
            window.setTimeout(function () {
                payOnlyCoins(hash, total_amount);
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


function getTokens() {
    token_count_rs = parseFloat($("#token_num").val().trim()) * 10
    $.ajax({
        url: "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=INR&tsyms=ETH",
        dataType: "json",
        success: function (data) {
            amount_tobe_payed = (data.RAW.INR.ETH.OPEN24HOUR * token_count_rs).toFixed(18);
            tx = send(token_contract.methods.payUser(), web.utils.toWei(amount_tobe_payed, "ether"))
        }
    });
}

async function refresh_account(){
    var curr_balance = await token_contract.methods.balanceOf(current_user_account).call()
    var donated_amount = await operations_contract.methods.donors_to_total_amount_donated(current_user_account).call()

    all_donations = await operations_contract.methods.get_donor_donations(current_user_account).call()

    $("#balance_amount").text(curr_balance / (10**18))
    $("#donated_amount").text(donated_amount / (10**18))

    for(var donation in all_donations){
        $("#donations_table").append(`
            <tr>
                <td>${all_donations[donation]["id"]}</td>
                <td>${all_donations[donation]["item_ids"]}</td>
                <td>${all_donations[donation]["item_qtys"]}</td>
                <td>${all_donations[donation]["total_amount"] / (10**18)}</td>
            </tr>
        `)
    }
}

async function place_donation(){
    confirmed_total = parseFloat($("#donate_coins").val()) * (10**18)
    transaction1 = token_contract.methods.approve(operations_contract_details[1], confirmed_total.toString())
    tx = await send(transaction1)
    payOnlyCoins(tx.toString(), confirmed_total)
}