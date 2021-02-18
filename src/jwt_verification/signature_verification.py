import json
import os.path
import requests
from hashlib import md5
import urllib3
import base64
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import logging
from Cryptodome.PublicKey import RSA
from jwkest.ecc import P256
from jwkest.ecc import P384
from jwkest.ecc import P521

import jwkest
from jwkest import jws, b64d_enc_dec
from jwkest import b64d, b64e

from jwkest.jwk import SYMKey, KEYS
from jwkest.jwk import ECKey
from jwkest.jwk import import_rsa_key_from_file
from jwkest.jwk import RSAKey
from jwkest.jws import SIGNER_ALGS, factory
from jwkest.jws import JWSig
from jwkest.jws import JWS
from config import load_config


class JWT_Verification():

    def __init__(self, url):
        self.SIGKEYS = KEYS()
        self.url = url
        keys_json = self.getKeys_JWT()
        self.SIGKEYS.load_dict(keys_json)

    def verify_signature_JWT(self, jwt):
        symkeys = [k for k in self.SIGKEYS if k.alg == "RS256"]

        _rj = JWS()
        info = _rj.verify_compact(jwt, symkeys)
        decoded_json = self.decode_JWT(jwt)

        if info == decoded_json:
            return True
        else:
            return False

    def getKeys_JWT(self):
        headers = { 'content-type': "application/json", "cache-control": "no-cache" }
        res = requests.get(self.url+"/oxauth/restv1/jwks", headers=headers, verify=False)
        json_dict = json.loads(res.text)
        return json_dict
    
    def decode_JWT(self, jwt):
        payload = str(jwt).split(".")[1]
        paddedPayload = payload + '=' * (4 - len(payload) % 4)
        decoded = base64.b64decode(paddedPayload)
        decoded_json = json.loads(decoded)
        return decoded_json