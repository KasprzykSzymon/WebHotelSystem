import base64
import hashlib
import hmac
import json

import requests
data_to_hash = "53c59ed5-64b8-44ee-8db7-3d0e555c5eea"
key = "70d0fac2-c3bf-43c1-b55f-208698e43eb7"

def calculate_hmac(data, key):
    hashed_object = hmac.new(key, data, hashlib.sha256).digest()
    return base64.b64encode(hashed_object)


hmac_hash = calculate_hmac(data_to_hash.encode(), key.encode())
# Example structure from API doc

def new_payment(data, idempotency_key):
    data = json.dumps(data)
    s = requests.Session()
    print(key)
    print(data)
    print(data_to_hash)
    req = requests.Request('POST', "https://api.sandbox.paynow.pl/v1/payments",
                           {'Api-key': key, "Signature": calculate_hmac(data.encode(), data_to_hash.encode()),
                            'Idempotency-Key': idempotency_key, 'Accept': '*/*', 'Content-Type': 'application/json'},
                           data=data).prepare()
    r = s.send(req)
    return (json.loads(r.text))


def check_payment(payment_id):
    s = requests.Session()
    req = requests.Request('GET', "https://api.sandbox.paynow.pl/v1/payments/{}/status".format(payment_id),
                           {'Api-key': key, 'Accept': '*/*', 'Content-Type': 'application/json'}).prepare()
    r = s.send(req)
    return (json.loads(r.text))
