import unittest
import sys
sys.path.append('..')
from api.globals import CREDENTIALS_PATH
import json

from api.app import create_app


class TestEndpointGetEmpty(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        with open(CREDENTIALS_PATH,"r") as cred_file:
            credentials = json.load(cred_file)
            self.headers = {'X-Dataverse-key': credentials["api_key"]}
        
    def test_get_mappings(self):
        response = self.client.get('/mapping')
        #print(response.json)
        self.assertEqual(response.status_code, 200)