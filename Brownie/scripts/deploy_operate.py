from brownie import KirshiOps, config, network
from scripts.helpfulScripts import getAccount


def deploy_ops():
    account = getAccount()
    deploy_tx = KirshiOps.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"])
    print(deploy_tx)


def add_goods(name, token_amount, image_uri, description):
    account = getAccount()
    KirshiOps = KirshiOps[-1]
    add_tx = KirshiOps.addGoods(
        name,
        token_amount,
        image_uri,
        description,
        {"from": account}
    )

    add_tx.wait(1)


def request_donation(farmer_address):
    account = getAccount()
    KirshiOps = KirshiOps[-1]
    request_tx = KirshiOps.requestDonation(farmer_address, [778], {"from": account})
    request_tx.wait(1)


def place_donation(donor_address):
    account = getAccount()
    KirshiOps = KirshiOps[-1]
    place_tx = KirshiOps.placeDonation(donor_address, [778], {"from": account})
    place_tx.wait(1)


def distribute_donation(donor_address):
    account = getAccount()
    KirshiOps = KirshiOps[-1]
    distribute_tx = KirshiOps.distributeDonation(donor_address, {"from": account})
    distribute_tx.wait(1)


def get_all_goods():
    KirshiOps = KirshiOps[-1]
    print(KirshiOps.getAllGoods())


def main():
    # deploy_KirshiOps()

    # add_goods("seeds", 10, "", "good quality seeds")
    # add_goods("tanker", 70, "", "water tanker")
    # add_goods("sprinkler", 50, "", "For proper spread of water")

    # get_all_goods()
    # request_donation("")
    # place_donation("")
    # place_donation("")
    # place_donation("")
    distribute_donation("")