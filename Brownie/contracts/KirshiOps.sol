// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/access/Ownable.sol";

contract KirshiOps is Ownable {
    uint256 private goods_counter = 777;

    Goods[] public all_goods;

    mapping(uint256 => Goods) public id_to_good;
    mapping(uint256 => address[]) public goods_to_farmers;
    mapping(uint256 => uint256) public goods_to_availability;
    mapping(address => uint256[]) public donors_to_goods;
    mapping(address => uint256[]) public farmer_to_allocations;
    mapping(uint256 => uint256[2]) public good_last_farmer_index;

    struct Goods {
        uint256 id;
        string name;
        uint256 token_amount;
        string image_uri;
        string description;
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
            if(goods_to_availability[good_ids[index]] > 0){
                farmer_to_allocations[farmer_address].push(good_ids[index]);
                goods_to_availability[good_ids[index]]--;
            }
            else{
                goods_to_farmers[good_ids[index]].push(farmer_address);
            }
        }
    }

    function placeDonation(address donor_address, uint256[] memory good_ids)
        public
    {
        for (uint256 index = 0; index < good_ids.length; index++) {
            donors_to_goods[donor_address].push(good_ids[index]);
            goods_to_availability[good_ids[index]]++;
        }
    }

    // Function to distribute the goods based on user donations
    function distributeDonation(address donor_address) public onlyOwner {
        for (uint256 good_index = 0; good_index < donors_to_goods[donor_address].length; good_index++) {

            uint256 curr_good_id = donors_to_goods[donor_address][good_index];
            uint256 available_good_quantity = goods_to_availability[curr_good_id];

            // When there is no requests
            if (goods_to_farmers[curr_good_id].length == 0) {
                continue;
            }
            // When the available good quantity is more than requested
            else if (available_good_quantity >= goods_to_farmers[curr_good_id].length) {
                for (uint256 farmer_index = 0; farmer_index < goods_to_farmers[curr_good_id].length; farmer_index++) {
                    farmer_to_allocations[goods_to_farmers[curr_good_id][farmer_index]].push(good_index);
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
                    farmer_to_allocations[goods_to_farmers[curr_good_id][cuur_farmer_index]].push(curr_good_id);

                    // Swap the allocated farmer with last member
                    goods_to_farmers[curr_good_id][cuur_farmer_index] = goods_to_farmers[curr_good_id][goods_to_farmers[curr_good_id].length - 1];

                    // Delete the last member
                    goods_to_farmers[curr_good_id].pop();

                    available_good_quantity--;

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
            delete donors_to_goods[donor_address][good_index];
        }

        delete donors_to_goods[donor_address];
    }


    function increaseGoodQuantity(
        uint256[] memory good_ids,
        uint256[] memory good_qts
    ) public onlyOwner{
        for (uint256 index = 0; index < good_ids.length; index++) {
            goods_to_availability[good_ids[index]] += good_qts[index];
        }
    }

    function getAllGoods() public view returns(Goods[] memory){
        return all_goods;
    }
}
