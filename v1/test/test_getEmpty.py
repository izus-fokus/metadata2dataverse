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
        response = self.client.get('/metadata/harvester')
        self.assertEqual(response.status_code, 200)
        
    def test_empty_metadata_engmeta(self):
        response = self.client.get('/metadata/engmeta')
        self.assertEqual(response.status_code, 200)

    def test_empty_metadata_engmeta_verbose(self):
        response = self.client.get('/metadata/engmeta?verbose=True')
        self.assertIn('warnings', response.json)
        self.assertEqual(response.status_code, 202)

    def test_empty_metadata_codemeta(self):
        response = self.client.get('/metadata/codemeta')
        self.assertEqual(response.status_code, 200)

    def test_empty_metadata_datacite(self):
        response = self.client.get('/metadata/datacite')
        self.assertEqual(response.status_code, 200)

    def test_empty_metadata_codemeta_edit(self):
        response = self.client.get('/metadata/codemeta?method=edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn("fields", response.json)
        self.assertIsInstance(response.json["fields"], list)

    def test_empty_metadata_codemeta_update(self):
        response = self.client.get('/metadata/codemeta?method=update')
        self.assertEqual(response.status_code, 200)
        self.assertIn("metadataBlocks", response.json)


    def test_empty_metadata_codemeta_create(self):
        response = self.client.get('/metadata/codemeta?method=create')
        self.assertEqual(response.status_code, 200)
        self.assertIn("datasetVersion", response.json)

        
