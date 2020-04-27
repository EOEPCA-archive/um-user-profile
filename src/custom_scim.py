#!/usr/bin/python3
import WellKnownHandler as wkh

import collections

class SCIMClient():

    def __init__(self, config):
        sso_url = self._get_valid_https_url(config["sso_url"])
        self.wkhandler = wkh.WellKnownHandler(sso_url,secure=not config["debug_mode"]) # Force HTTPS if not debug mode

        self.protected_attrs = config["protected_attributes"]
        self.blacklist_attrs = config["blacklist_attributes"]
        self.separator = config["separator_ui_attributes"]

        # If we don't have a client, auto-create one in SCIM
        if config["client_id"] == "" or config["client_secret"] == "":
            # TODO: Init / Register

            config["client_id"] = "@!C28A.A0EC.7CA4.6154!0001!94C2.0974!0008!060F.1277.5535.6112"
            config["client_secret"] = "ca32d9bd-2416-4713-8627-6965e36dd4ac"
            config["scopes"] = 'openid oxd permission uma_protection'.split()


    def _get_valid_https_url(self, url):
        if "http" not in url:
            return "https://" + url

    def changeAttributes(self, user_id, data):
        #TODO: SCIM LIBRARY CALL

        pass


    def getAttributes(self, user_id):
        err = ""
        code = ""

        #TODO: SCIM LIBRARY CALL

        data = {'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'], 'id': '@!C28A.A0EC.7CA4.6154!0001!94C2.0974!0000!F237.2B41.BAB1.7A00', 'meta': {'resourceType': 'User', 'created': '2020-04-16T16:33:44.208Z', 'lastModified': '2020-04-21T18:47:29.649Z', 'location': 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users/@!C28A.A0EC.7CA4.6154!0001!94C2.0974!0000!F237.2B41.BAB1.7A00'}, 'userName': 'tiago@test.com', 'name': {'familyName': 'M Fernandes', 'givenName': 'Tiago', 'middleName': 'M', 'formatted': 'Tiago Fernandes'}, 'displayName': 'Tiago', 'active': True, 'emails': [{'value': 'tiago@test.com', 'primary': False}]}

        return self._clean_attributes(data), err, code

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