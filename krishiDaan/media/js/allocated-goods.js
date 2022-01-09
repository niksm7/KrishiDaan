const web = new Web3("https://speedy-nodes-nyc.moralis.io//polygon/mumbai")
token_contract_details = JSON.parse(localStorage.getItem("token_contract"))
operations_contract_details = JSON.parse(localStorage.getItem("operations_contract"))
var token_contract = new web.eth.Contract(token_contract_details[0], token_contract_details[1])
var operations_contract = new web.eth.Contract(operations_contract_details[0], operations_contract_details[1])

async function get_allocated_goods(){
    all_good_ids = await operations_contract.methods.getFarmerAllocations(farmer_address).call()
    for(var good in all_good_ids){
        curr_good_id = all_good_ids[good]["id"]
        good_quantity = await operations_contract.methods.farmer_to_allocations_quantities(farmer_address, curr_good_id).call()
        $("#allocations_row").append(`
        <div class="col">
            <div class="card" style="width: 20rem;border-radius: 16px;">
                <img class="card-img-top" src="${all_good_ids[good]["image_uri"]}" alt="Card image cap">
                <div class="card-block" style="text-align: center;">
                    <h4 class="card-title">${all_good_ids[good]["name"]}</h4>
                    <dl>
                        <dt><p class="card-text" style="font-size: 20px;font-weight: 800;">Price: ${all_good_ids[good]["token_amount"] / (10**18)} KC</p></dt>
                        <dd><p class="card-text">Qty Allocated: ${good_quantity}</p></dd>
                    </dl>
                </div>
            </div>
        </div>
        `)
    }
}

get_allocated_goods()