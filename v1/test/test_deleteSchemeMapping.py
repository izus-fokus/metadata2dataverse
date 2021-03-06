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
        
    def test_deleteSchemeMapping(self):
        response = self.client.delete('/mapping/harvester?format=plain/txt')
        self.assertEqual(response.status_code, 204)
        
        response = self.client.delete('/mapping/engmeta?format=text/xml')
        self.assertEqual(response.status_code, 204)
        
        response = self.client.delete('/mapping/blubb')
        self.assertEqual(response.status_code, 404)
        
        response = self.client.delete('/mapping/engmeta?format=blub')
        self.assertEqual(response.status_code, 400)
        