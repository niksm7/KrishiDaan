from brownie import KrishiOps, config, network, KrishiCoin
from scripts.helpfulScripts import getAccount


def deploy_KrishiOps():
    account = getAccount()
    deploy_tx = KrishiOps.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"])
    print(deploy_tx)


def add_goods(name, token_amount, image_uri, description):
    account = getAccount()
    KrishiOps = KrishiOps[-1]
    add_tx = KrishiOps.addGoods(
        name,
        token_amount,
        image_uri,
        description,
        {"from": account}
    )

    add_tx.wait(1)


def request_donation(farmer_address):
    account = getAccount()
    KrishiOps = KrishiOps[-1]
    request_tx = KrishiOps.requestDonation(farmer_address, [778], {"from": account})
    request_tx.wait(1)


def place_donation(donor_address):
    account = getAccount()
    KrishiOps = KrishiOps[-1]
    place_tx = KrishiOps.placeDonation(donor_address, [778], {"from": account})
    place_tx.wait(1)


def distribute_donation(donor_address):
    account = getAccount()
    KrishiOps = KrishiOps[-1]
    distribute_tx = KrishiOps.distributeDonation(donor_address, {"from": account})
    distribute_tx.wait(1)


def get_all_goods():
    KrishiOps = KrishiOps[-1]
    print(KrishiOps.getAllGoods())


def main():
    deploy_KrishiOps()

    # add_goods("seeds", 10, "", "good quality seeds")
    # add_goods("tanker", 70, "", "water tanker")
    # add_goods("sprinkler", 50, "", "For proper spread of water")

    # get_all_goods()
    # request_donation("")
    # place_donation("")
    # place_donation("")
    # place_donation("")
    distribute_donation("")