import unittest
import sys
sys.path.append('..')
import requests
from lxml import etree as ET
import json

from api.app import create_app


class TestEndpointGetEmpty(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.headers = {'X-Dataverse-key': '0f72c986-defc-486b-afe7-d4524d7d3c17'}
        
    def test_createSchemeMapping(self):
        with open(r'./input/new_mapping.yaml', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/mapping', data=file_content, headers={'Content-Type':'application/yaml'})
        self.assertEqual(response.status_code, 201)
        