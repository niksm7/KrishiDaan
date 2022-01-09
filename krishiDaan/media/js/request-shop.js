const web = new Web3("https://rinkeby.infura.io/v3/")
token_contract_details = JSON.parse(localStorage.getItem("token_contract"))
operations_contract_details = JSON.parse(localStorage.getItem("operations_contract"))
var token_contract = new web.eth.Contract(token_contract_details[0], token_contract_details[1])
var operations_contract = new web.eth.Contract(operations_contract_details[0], operations_contract_details[1])

async function display_goods() {
    var all_goods = await operations_contract.methods.getAllGoods().call();
    for(var good in all_goods){
        var waiting = await operations_contract.methods.goods_to_waiting(all_goods[good]["id"]).call()
        var availability = await operations_contract.methods.goods_to_availability(all_goods[good]["id"]).call()
        console.log(waiting, availability)
        if(waiting <= availability){
            if(availability > 0){
                waiting = "Available!"
            }
            else{
                waiting = "Waiting: " + 1
            }
        }
        else{
            waiting = "Waiting: " + waiting
        }

        $("#goods_row").append(`
        <div class="col">
            <div class="card" style="width: 20rem;border-radius: 16px;">
                <img class="card-img-top" src="${all_goods[good]["image_uri"]}"
                    alt="Card image cap">
                <div class="card-block" style="text-align: center;">
                    <h4 class="card-title">${all_goods[good]["name"]}</h4>
                    <p class="card-text"  style="font-size: 20px;font-weight: 800;">Price: ${all_goods[good]["token_amount"] / (10**18)}</p>
                    <p class="card-text" id="waiting${all_goods[good]["id"]}">${waiting}</p>
                    <a href="#" data-name="${all_goods[good]["name"]}" data-goodid="${all_goods[good]["id"]}" data-price="${all_goods[good]["token_amount"]}" class="add-to-cart btn" style="background-color:#84A98C; color:white;width: 85%;">Request</a>
                </div>
            </div>
        </div>
        `)

        if (waiting == "Available!") {
            $(`#waiting${all_goods[good]["id"]}`).css({"color":"green"})
        }
        else{
            $(`#waiting${all_goods[good]["id"]}`).css({"color":"red"})
        }
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

display_goods()