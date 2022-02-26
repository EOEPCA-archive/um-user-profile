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
            f = open("/2.txt", "a")
            f.write("GOOGo:  ")
            f.write("http://"+ self.pep_url + "/resources")
            f.write("    " + str(self.create_bearer_header(token)))
            data= requests.get("http://"+ self.pep_url + "/resources", headers=self.create_bearer_header(token))
            f.write(str(data))
            f.write(str(data.json()))
            f.close()
        except Exception as e:
            err = "Something went wrong while getting resources: "+str(e)
            data = {}
            return data, err
        return data, err

    def get_policies(self, resource_id, token):
        err = ""
        data={}
        try:
            f = open("/3.txt", "a")
            f.write("policies:  ")
            f.write("http://"+ self.pdp_url + "/policy/")
            f.write("    " + str(self.create_bearer_header(token)))
            data_resource_id = {'resource_id': str(resource_id)}
            f.write(str(data_resource_id))
            data= requests.get("http://"+ self.pdp_url + "/policy/", json = data_resource_id, headers=self.create_bearer_header(token))
            f.write(str(data))
            f.write(str(data.json()))
            f.close()
        except Exception as e:
            err = "Something went wrong while getting resources: "+str(e)
            data = {}
            return data, err
        return data, err