// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract KirshiOps is Ownable,VRFConsumerBase {
    uint256 public fee;
    bytes32 public keyhash;
    uint256 private goods_counter = 777;

    Goods[] public all_goods;

    mapping(uint256 => Goods) public id_to_good;
    mapping(uint256 => address[]) public goods_to_farmers;
    mapping(uint256 => uint256) public goods_to_availability;
    mapping(address => uint256[]) public donors_to_goods;

    struct Goods {
        uint256 id;
        string name;
        uint256 token_amount;
        string image_uri;
        string description;
    }

    constructor(
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    )public VRFConsumerBase(_vrfCoordinator, _link){
        fee = _fee;
        keyhash = _keyhash;
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
        goods_counter ++;
    }


    function requestDonation(
        address farmer_address,
        uint256[] memory good_ids
    ) public{
        for (uint256 index = 0; index < good_ids.length; index++) {
            goods_to_farmers[good_ids[index]].push(farmer_address);
        }
    }


    function placeDonation(
        address donor_address,
        uint256[] memory good_ids
    ) public{
        for (uint256 index = 0; index < good_ids.length; index++) {
            donors_to_goods[donor_address].push(good_ids[index]);
            goods_to_availability[good_ids[index]]++;
        }

        // Call random function
        bytes32 requestId = requestRandomness(keyhash, fee);
    }


    // Get Random number and perform actions
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override{
    }
}