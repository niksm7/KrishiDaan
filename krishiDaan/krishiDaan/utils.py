import os
import json
from eth_typing import abi
import requests
from web3.middleware import geth_poa_middleware
from web3 import Web3
from dotenv import load_dotenv
from django.core.files.storage import default_storage
from pathlib import Path

load_dotenv()

infura_url = "https://rinkeby.infura.io/v3/"

web = Web3(Web3.HTTPProvider(infura_url))
web.middleware_onion.inject(geth_poa_middleware, layer=0)

web.eth.default_account = web.eth.account.privateKeyToAccount(os.getenv("PRIVATE_KEY")).address

# Operations
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

operations_abi = requests.get("https://api-rinkeby.etherscan.io/api?module=contract&action=getabi&address=&apikey=", headers=headers).json()['result']

operations_address = ""

operations_contract = web.eth.contract(abi=operations_abi, address=operations_address)

# Token
token_address = ""


def upload_to_ipfs(_image):
    ipfs_url = "http://127.0.0.1:5001"
    end_point = "/api/v0/add"

    # upload
    response = requests.post(ipfs_url + end_point, files={"file": _image})
    image_uri = pin_to_pinata(_image)
    return image_uri


def pin_to_pinata(_image):
    default_storage.save(str(_image), _image)
    file_path = default_storage.path(str(_image))
    PINATA_BASE_URL = "https://api.pinata.cloud/"
    endpoint = "pinning/pinFileToIPFS"
    filename = str(_image)
    headers = {
        "pinata_api_key": os.getenv("PINATA_API_KEY"),
        "pinata_secret_api_key": os.getenv("PINATA_API_SECRET"),
    }
    with Path(file_path).open("rb") as fp:
        image_binary = fp.read()
        response = requests.post(
            PINATA_BASE_URL + endpoint,
            files={"file": (filename, image_binary)},
            headers=headers,
        )
        default_storage.delete(filename)
        img_uri = "https://gateway.pinata.cloud/ipfs/" + response.json()["IpfsHash"]
        return img_uri
