#!/usr/bin/python3
import requests
import json
import WellKnownHandler as wkh

import generic

class OAuthClient():

    def __init__(self, config,use_env_var):
        if use_env_var is False:
            self.scopes = self._get_valid_url_scopes(config["scopes"])
        else:
            config["scopes"] = config["scopes"].split(" ")
            self.scopes = self._get_valid_url_scopes(config["scopes"])

        sso_url = self._get_valid_https_url(config["sso_url"])
        self.wkhandler = wkh.WellKnownHandler(sso_url,secure=not config["debug_mode"]) # Force HTTPS if not debug mode
        self.client_id = self._get_valid_url_client_id(config["client_id"])
        self.redirect_uri = config["redirect_uri"]
        self.client_secret = config["client_secret"]
        self.post_logout_redirect_uri = config["post_logout_redirect_uri"]

    def _get_valid_url_client_id(self, client_id):
        return client_id.replace("@","%40")

    def _get_valid_url_scopes(self, scopes):
        return_scopes = ""
        for scope in scopes:
            return_scopes = return_scopes + scope + "%20"
        return_scopes = return_scopes.rstrip("%20")

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
