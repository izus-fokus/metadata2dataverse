import unittest
import sys
sys.path.append('..')
import requests
from lxml import etree as ET
import json

from api.app import create_app


class TestEndpointGetEmpty(unittest.TestCase):
    def setUp(self):
        #self.__init__()
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.headers = {'X-Dataverse-key': '0f72c986-defc-486b-afe7-d4524d7d3c17'}

    def test_empty_metadata_harvester(self):
        response = self.client.get('/metadata/harvester?verbose=True')
        self.assertIn('warnings', response.json)
        print(response.json['warnings'])
        self.assertEqual(response.status_code, 202)
        
    def test_empty_metadata_engmeta(self):
        response = self.client.get('/metadata/engmeta?verbose=True')
        print(response.json['warnings'])
        self.assertEqual(response.status_code, 202)