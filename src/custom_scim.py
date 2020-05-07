#!/usr/bin/python3
from eoepca_scim import *
import collections

class SCIMClient():

    def __init__(self, config):
        sso_url = self._get_valid_https_url(config["sso_url"])

        self.protected_attrs = config["protected_attributes"]
        self.blacklist_attrs = config["blacklist_attributes"]
        self.separator = config["separator_ui_attributes"]

        # auto-create client in SCIM
        self.scim_client = EOEPCA_Scim(sso_url)
        grantTypes=["client_credentials", "urn:ietf:params:oauth:grant-type:uma-ticket"]
        redirectURIs=["https://demoexample.gluu.org/login"]
        logoutURI="https://demoexample.gluu.org/logout"
        responseTypes=[]
        scopes=["openid", "oxd", "permission"]
        self.scim_client.registerClient("TestClient", grantTypes, redirectURIs, logoutURI, responseTypes, scopes)

    def _get_valid_https_url(self, url):
        if "http" not in url:
            return "https://" + url

    def changeAttributes(self, user_id, data):
        data = data.to_dict()
        for k, v in data.items():
            if k in self.protected_attrs:
                continue
            if self.separator in k:
                tmp = k.split(self.separator)
                k = '.'.join(tmp)
            res = self.scim_client.editUserAttribute(user_id,k,v)
            if res != 200:
                print(res)
                print("error for "+str(k))
                return "Error while updating "+str(k)+" -> "+str(res), ""

        return "", ""


    def getAttributes(self, user_id):
        err = ""
        try:
            data = self.scim_client.getUserAttributes(user_id)
            print(data)
        except Exception as e:
            print(str(e))
            err = "Something went wrong while getting attributes: "+str(e)
            data = {}
            return {}, err

        return self._clean_attributes(data), err

    def _clean_attributes(self, data):

        ret = {"fixed": {},
               "editable": {}}
        data = self._purge_blacklist(data)

        for k,v in data.items():
            if isinstance(v, dict):
                for k,v in self._flatten({k:v}).items():
                    if k in self.protected_attrs:
                        ret["fixed"][k] = v
                    else:
                        ret["editable"][k] = v

            if k in self.protected_attrs:
                ret["fixed"][k] = v
            else:
                ret["editable"][k] = v

        return ret

    def _purge_blacklist(self, data):
        delete = []
        for k,v in data.items():
            if k in self.blacklist_attrs:
                delete.append(k)
            if isinstance(v, dict):
                data[k] = self._purge_blacklist(v)

        for k in delete: del data[k]

        return data

    def _flatten(self, d, parent_key=''):
        items = []
        for k, v in d.items():
            new_key = parent_key + self.separator + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(self._flatten(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def deleteUser(self,userID):
        
        try:
            self.scim_client.deleteUser(userID)
        except Exception as e:
            print(str(e))
            err = "Something went wrong while deleting user: "+str(e)

