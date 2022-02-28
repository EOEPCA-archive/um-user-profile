import requests
import logging

'''
    Class to deal with PEP and PDP endpoints calls
'''
class PEP_Handler:

    def __init__(self, pep_url: str, pdp_url: str):
        logging.info("Connecting to PEP and PDP endpoints...")
        self.pep_url = pep_url
        self.pdp_url = pdp_url

    def create_bearer_header(self, token):
        return { 'content-type': 'application/json', 'Authorization' : 'Bearer '+token}

    def get_resources(self, token):
        err = ""
        data={}
        try:
            data= requests.get("http://"+ self.pep_url + "/resources", headers=self.create_bearer_header(token))
        except Exception as e:
            err = "Something went wrong while getting resources: "+str(e)
            data = {}
            return data, err
        return data, err

    def get_policies(self, resource_id, token):
        err = ""
        data={}
        try:
            data_resource_id = {'resource_id': str(resource_id)}
            data= requests.get("http://"+ self.pdp_url + "/policy/", json = data_resource_id, headers=self.create_bearer_header(token))
        except Exception as e:
            err = "Something went wrong while getting resources: "+str(e)
            data = {}
            return data, err
        return data, err