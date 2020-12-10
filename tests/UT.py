#!/usr/bin/env python3
import unittest
import os
import requests
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')

def test_running_service():
    resp=requests.get('https://test.10.0.2.15.nip.io/web_ui/profile_management', verify=False)
    if resp.status_code ==200: resp=requests.get('https://test.10.0.2.15.nip.io/web_ui/apis_management', verify=False)
    if resp.status_code ==200: resp=requests.get('https://test.10.0.2.15.nip.io/web_ui/licenses_management', verify=False)
    if resp.status_code ==200:
        resp=requests.get('https://test.10.0.2.15.nip.io/web_ui/apis_management', verify=False)
        logging.info('All endpoints are up                 '+ str(resp.status_code))
    return resp.status_code

class UT(unittest.TestCase):
    
    def test_01_service(self):
        requests.packages.urllib3.disable_warnings() 

        #self.assertEqual(mymodule.sum(5, 7), 12)
        resp=requests.get('https://test.10.0.2.15.nip.io/web_ui', verify=False)
        if resp.status_code==200:
            logging.info("The Web UI service is running        " + str(resp.status_code))
            self.assertEqual(test_running_service(),200)
        else:
            logging.info('The Web UI service is not running    ' + str(resp.status_code))

class OT(unittest.TestCase):
    
    def test_02_functionality(self):
        print('Functionality')

if __name__ == "__main__":
    unittest.main()
