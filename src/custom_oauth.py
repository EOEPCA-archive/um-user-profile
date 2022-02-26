#!/usr/bin/python3
import requests
import base64
import json
from eoepca_scim import *
import logging
import WellKnownHandler as wkh
from base64 import b64encode
import generic
from jwkest.jws import JWS
from jwkest.jwk import SYMKey, KEYS
from jwkest.jwk import RSAKey, import_rsa_key_from_file, load_jwks_from_url, import_rsa_key
from jwkest.jwk import load_jwks
from jwkest.jwk import rsa_load
from Crypto.PublicKey import RSA
from jwt_verification.signature_verification import JWT_Verification


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class OAuthClient(metaclass=Singleton):
    def __init__(self, config,use_env_var):
        if use_env_var is False:
            self.scopes = self._get_valid_url_scopes(config["scopes"])
        else:
            config["scopes"] = config["scopes"].split(" ")
            self.scopes = self._get_valid_url_scopes(config["scopes"])
        sso_url = self._get_valid_https_url(config["sso_url"])
        self.url= sso_url
        self.wkhandler = wkh.WellKnownHandler(sso_url,secure=not config["debug_mode"]) # Force HTTPS if not debug mode

        scim_client2 = EOEPCA_Scim(sso_url)
        grantTypes=["client_credentials", "urn:ietf:params:oauth:grant-type:uma-ticket", "authorization_code", "refresh_token", "implicit", "password"]
        redirectURIs=["https://"+config["sso_url"]+"/web_ui/oauth/callback"]
        logoutURI="http://"+config["sso_url"]+"/web_ui"
        responseTypes=["code", "token", "id_token"]
        scopes=["openid", "user_name", "permission", "email", "eoepca", "is_operator"]
        sectorIdentifier="https://"+config["sso_url"]+"/oxauth/sectoridentifier/9b473868-fa96-4fd1-a662-76e3663c9726"
        token_endpoint_auth_method=ENDPOINT_AUTH_CLIENT_POST
        scim_client2.registerClient("UserClient", grantTypes, redirectURIs, logoutURI, responseTypes, scopes, token_endpoint_auth_method, sectorIdentifier=sectorIdentifier, subject_type= "public")

        self.client_id = self._get_valid_url_client_id(scim_client2.client_id)
        self.redirect_uri = config["redirect_uri"]
        self.client_secret = scim_client2.client_secret
        self.post_logout_redirect_uri = config["post_logout_redirect_uri"]

    def _get_valid_url_client_id(self, client_id):
        return client_id.replace("@","%40")

    def _get_valid_url_scopes(self, scopes):
        return_scopes = ""
        for scope in scopes:
            return_scopes = return_scopes + scope + "%20"
        return_scopes = return_scopes.rstrip("%20")
        if "is_operator" not in str(return_scopes):
            return_scopes=return_scopes+"%20is_operator"
        return return_scopes

    def _get_valid_https_url(self, url):
        if "http" not in url:
            return "https://" + url

    def get_login_url(self):
        auth_endpoint = self.wkhandler.get(wkh.TYPE_OIDC, wkh.KEY_OIDC_AUTHORIZATION_ENDPOINT)

        return auth_endpoint + "?scope="+self.scopes+"&client_id="+self.client_id+"&redirect_uri="+self.redirect_uri+"&response_type=code"

    def get_token(self, code):
        token_endpoint = self.wkhandler.get(wkh.TYPE_OIDC, wkh.KEY_OIDC_TOKEN_ENDPOINT)

        payload = "grant_type=authorization_code&client_id="+self.client_id+"&code="+code+"&client_secret="+self.client_secret+"&scope="+self.scopes+"&redirect_uri="+self.redirect_uri
        headers = {"content-type": "application/x-www-form-urlencoded", 'cache-control': "no-cache"}
        
        response = requests.request("POST", token_endpoint, data=payload, headers=headers, verify=False)
        self.isOperator = self.verify_uid_headers(self.url, json.loads(response.text),'isOperator')
        return json.loads(response.text)

    def refresh_token(self, refresh_token):
        "Gets a new token, using a previous refresh token"
        token_endpoint = self.wkhandler.get(wkh.TYPE_OIDC, wkh.KEY_OIDC_TOKEN_ENDPOINT)

        payload = "grant_type=refresh_token&refresh_token="+refresh_token+"&client_id="+self.client_id+"&client_secret="+self.client_secret
        headers = {"content-type": "application/x-www-form-urlencoded", 'cache-control': "no-cache"}
        
        response = requests.request("POST", token_endpoint, data=payload, headers=headers, verify=False)
        return json.loads(response.text)

    def get_user_info(self,access_token):
        user_info_endpoint = self.wkhandler.get(wkh.TYPE_OIDC, wkh.KEY_OIDC_USERINFO_ENDPOINT)

        response = requests.request("GET", user_info_endpoint+"?access_token="+access_token, verify=False)
        status = response.status_code
        if status > 199 and status < 300:
            return json.loads(response.text)
        else:
            return None

    def end_session_url(self, id_token):
        end_session_endpoint = self.wkhandler.get(wkh.TYPE_OIDC, wkh.KEY_OIDC_END_SESSION_ENDPOINT)

        return end_session_endpoint +"?post_logout_redirect_uri="+self.post_logout_redirect_uri+"&id_token_hint="+id_token
    

    def verify_JWT_token(self,url, token, key):
        try:
            header = str(token).split(".")[0]
            paddedHeader = header + '=' * (4 - len(header) % 4)
            decodedHeader = base64.b64decode(paddedHeader)
            #to remove byte-code
            decodedHeader_format = decodedHeader.decode('utf-8')
            decoded_str_header = json.loads(decodedHeader_format)

            payload = str(token).split(".")[1]
            paddedPayload = payload + '=' * (4 - len(payload) % 4)
            decoded = base64.b64decode(paddedPayload)
            #to remove byte-code
            decoded = decoded.decode('utf-8')
            decoded_str = json.loads(decoded)
            if decoded_str_header['kid'] != "RSA1":
                verificator = JWT_Verification(url)
                result = verificator.verify_signature_JWT(token)
            else:
                #validate signature for rpt
                rsajwk = RSAKey(kid="RSA1", key=import_rsa_key_from_file("config/public.pem"))
                dict_rpt_values = JWS().verify_compact(token, keys=[rsajwk], sigalg="RS256")

                if dict_rpt_values == decoded_str:
                    result = True
                else:
                    result = False

            if result == False:
                print("Verification of the signature for the JWT failed!")
                raise Exception
            else:
                print("Signature verification is correct!")

            if decoded_str_header['kid'] != "RSA1":
                if key in decoded_str.keys():
                    if decoded_str[key] != None:
                        user_value = decoded_str[key]
                    else:
                        raise Exception
                else:
                    user_value = decoded_str['pct_claims'][key]
            else:
                if decoded_str[key] == None:
                    
                    if decoded_str['pct_claims'][key][0] == None:
                        raise Exception
                    else:
                        user_value = decoded_str['pct_claims'][key][0]
                else:
                    
                    user_value = decoded_str[key]

            return user_value
        except Exception as e:
            print("Authenticated RPT Resource. No Valid JWT id token passed! " +str(e))
            return None

    def verify_OAuth_token(self, token, key):
        headers = { 'content-type': "application/json", 'Authorization' : 'Bearer '+token}
        url = self.wkh.get(TYPE_OIDC, KEY_OIDC_USERINFO_ENDPOINT )
        try:
            res = get(url, headers=headers, verify=False)
            user = (res.json())
            return user[key]
        except:
            print("OIDC Handler: Get User "+key+": Exception occured!")
            return None

    def verify_uid_headers(self,url, jwt, key):
        value = None
        token_protected = None
        myJWT = jwt['id_token']
        value=self.verify_JWT_token(url, myJWT, key)
        return value
        
