from brownie import network, accounts, config


def getAccount(index=None, id=None, from_key="from_key1"):
    if index:
        return accounts[0]

    if id:
        return accounts.load(id)

    return accounts.add(config["wallets"][from_key])
