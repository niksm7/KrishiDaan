// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract KrishiOps is Ownable {
    uint256 private goods_counter = 777;
    uint256 private donation_counter = 123;
    uint256 public available_coins = 0;
    address private contract_owner;

    Goods[] public all_goods;
    Donations[] public all_donations;

    mapping(uint256 => Goods) public id_to_good;
    mapping(uint256 => address[]) public goods_to_farmers;
    mapping(uint256 => uint256) public goods_to_availability;
    mapping(address => Goods[]) public farmer_to_allocations;
    mapping(address => mapping(uint256 => uint256)) public farmer_to_allocations_quantities;
    mapping(uint256 => uint256[2]) public good_last_farmer_index;
    mapping(uint256 => Donations) public id_to_donations;
    mapping(address => Donations[]) public donors_to_donations;
    mapping(address => uint256) public donors_to_total_amount_donated;
    mapping(uint256 => uint256) public goods_to_waiting;

    struct Goods {
        uint256 id;
        string name;
        uint256 token_amount;
        string image_uri;
        string description;
    }

    struct Donations {
        uint256 id;
        address donor_address;
        string item_ids;
        string item_qtys;
        uint256 total_amount;
    }

    constructor(){
        contract_owner = msg.sender;
    }

    function addGoods(
        string memory _name,
        uint256 _token_amount,
        string memory _image_uri,
        string memory _description
    ) public {
        Goods memory new_good = Goods(
            goods_counter,
            _name,
            _token_amount,
            _image_uri,
            _description
        );
        id_to_good[goods_counter] = new_good;
        all_goods.push(new_good);
        goods_counter++;
    }

    function requestDonation(address farmer_address, uint256[] memory good_ids)
        public
    {
        for (uint256 index = 0; index < good_ids.length; index++) {
            if(goods_to_availability[good_ids[index]] > 0 && goods_to_waiting[good_ids[index]]==0){
                farmer_to_allocations[farmer_address].push(id_to_good[good_ids[index]]);
                farmer_to_allocations_quantities[farmer_address][good_ids[index]]++;
                goods_to_availability[good_ids[index]]--;
            }
            else{
                goods_to_farmers[good_ids[index]].push(farmer_address);
                goods_to_waiting[good_ids[index]]++;
            }
        }
    }

    function placeDonation(address payment_token, address donor_address, uint256[] memory _goods_ids, uint256[] memory _good_quantities, string memory _str_goods_ids, string memory _str_good_quantities)
        public
    {
        IERC20 paymentToken = IERC20(payment_token);
        uint256 _total_amount = 0;

        for (uint256 index = 0; index < _goods_ids.length; index++) {
            _total_amount += (id_to_good[_goods_ids[index]].token_amount * _good_quantities[index]);
        }

        require(
            paymentToken.allowance(donor_address, address(this)) >=
                _total_amount,
            "Allowance is not enought"
        );

        donateCoins(payment_token, donor_address, _total_amount, 1);

        for (uint256 good_index = 0; good_index < _goods_ids.length; good_index++) {
            goods_to_availability[_goods_ids[good_index]] += _good_quantities[good_index];
        }

        Donations memory new_donation = Donations(
            donation_counter,
            donor_address,
            _str_goods_ids,
            _str_good_quantities,
            _total_amount
        );

        id_to_donations[donation_counter] = new_donation;
        all_donations.push(new_donation);
        donors_to_donations[donor_address].push(new_donation);

        donors_to_total_amount_donated[donor_address] += _total_amount;

        donation_counter++;

    }

    // Function to distribute the goods based on user donations
    function distributeDonation(uint256[] memory available_goods) public onlyOwner {
        for (uint256 good_index = 0; good_index < available_goods.length; good_index++) {

            uint256 curr_good_id = available_goods[good_index];
            uint256 available_good_quantity = goods_to_availability[curr_good_id];

            // When there is no requests
            if (goods_to_farmers[curr_good_id].length == 0) {
                continue;
            }
            // When the available good quantity is more than requested
            else if (available_good_quantity >= goods_to_farmers[curr_good_id].length) {
                for (uint256 farmer_index = 0; farmer_index < goods_to_farmers[curr_good_id].length; farmer_index++) {
                    farmer_to_allocations[goods_to_farmers[curr_good_id][farmer_index]].push(id_to_good[curr_good_id]);
                    farmer_to_allocations_quantities[goods_to_farmers[curr_good_id][farmer_index]][curr_good_id]++;
                    available_good_quantity--;
                }
                delete goods_to_farmers[curr_good_id];
                good_last_farmer_index[curr_good_id][0] = 0;
                good_last_farmer_index[curr_good_id][1] = 0;
            } else {
                uint256 cuur_farmer_index = good_last_farmer_index[curr_good_id][0];
                uint256 reverse = 0;

                // If we are ahead of last index and there are still elements left we reverse
                if (cuur_farmer_index > goods_to_farmers[curr_good_id].length - 1 && goods_to_farmers[curr_good_id].length > 0) {
                    reverse = 1;
                    cuur_farmer_index = goods_to_farmers[curr_good_id].length - 1;
                    good_last_farmer_index[curr_good_id][1] = 1;
                }

                if (reverse != 1 && good_last_farmer_index[curr_good_id][1] == 1) {
                    reverse = 1;
                }

                while (available_good_quantity != 0) {
                    farmer_to_allocations[goods_to_farmers[curr_good_id][cuur_farmer_index]].push(id_to_good[curr_good_id]);

                    farmer_to_allocations_quantities[goods_to_farmers[curr_good_id][cuur_farmer_index]][curr_good_id]++;

                    // Swap the allocated farmer with last member
                    goods_to_farmers[curr_good_id][cuur_farmer_index] = goods_to_farmers[curr_good_id][goods_to_farmers[curr_good_id].length - 1];

                    // Delete the last member
                    goods_to_farmers[curr_good_id].pop();

                    available_good_quantity--;
                    goods_to_waiting[curr_good_id]--;

                    if (reverse == 0) {
                        cuur_farmer_index++;
                    } else {
                        cuur_farmer_index--;
                    }

                    // If we are ahead of last index and there are still elements left we reverse
                    if (reverse != 1 && cuur_farmer_index > goods_to_farmers[curr_good_id].length - 1 && goods_to_farmers[curr_good_id].length > 0) {
                        reverse = 1;
                        cuur_farmer_index--;
                        good_last_farmer_index[curr_good_id][1] = 1;
                    }
                }
                good_last_farmer_index[curr_good_id][0] = cuur_farmer_index;
            }

            goods_to_availability[curr_good_id] = available_good_quantity;
        }

    }


    function increaseGoodQuantity(
        uint256[] memory good_ids,
        uint256[] memory good_qts,
        uint256 new_amount_available
    ) public onlyOwner{
        for (uint256 index = 0; index < good_ids.length; index++) {
            goods_to_availability[good_ids[index]] += good_qts[index];
        }
        available_coins = new_amount_available;
    }


    function getAllGoods() public view returns(Goods[] memory){
        return all_goods;
    }


    function getAllDonations() public view returns(Donations[] memory){
        return all_donations;
    }

    function getFarmerAllocations(address _farmer_address) public view returns(Goods[] memory){
        return farmer_to_allocations[_farmer_address];
    }

    function get_donor_donations(address _donor_address) public view returns(Donations[] memory){
        return donors_to_donations[_donor_address];
    }


    function donateCoins(address payment_token, address donor_address, uint256 amount_of_tokens, uint256 is_internal) public{
        IERC20 paymentToken = IERC20(payment_token);
        require(
            paymentToken.transferFrom(
                msg.sender,
                contract_owner,
                amount_of_tokens
            ),
            "transfer Failed"
        );

        if(is_internal != 1){
            donors_to_total_amount_donated[donor_address] += amount_of_tokens;
            available_coins += amount_of_tokens;
            Donations memory new_donation = Donations(
                donation_counter,
                donor_address,
                "-",
                "-",
                amount_of_tokens
            );
            donors_to_donations[donor_address].push(new_donation);
        }
    }
}
