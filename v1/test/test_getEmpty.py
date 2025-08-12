import unittest
import sys
sys.path.append('..')
import requests
from lxml import etree as ET
import json
from api.globals import CREDENTIALS_PATH

from api.app import create_app


class TestEndpointGetEmpty(unittest.TestCase):
    def setUp(self):
        #self.__init__()
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        with open(CREDENTIALS_PATH,"r") as cred_file:
            credentials = json.load(cred_file)
            self.headers = {'X-Dataverse-key': credentials["api_key"]}
            self.dataverse_url = credentials["base_url"]
            self.dataset = credentials["dataset_id"]

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
        response = self.client.get('/metadata/codemeta20')
        self.assertEqual(response.status_code, 200)

    def test_empty_metadata_datacite(self):
        response = self.client.get('/metadata/datacite')
        self.assertEqual(response.status_code, 200)

    def test_empty_metadata_codemeta_edit(self):
        response = self.client.get('/metadata/codemeta20?method=edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn("fieldsElement", response.json)
        self.assertIsInstance(response.json["fieldsElement"], list)

    def test_empty_metadata_codemeta_update(self):
        response = self.client.get('/metadata/codemeta20?method=update')
        self.assertEqual(response.status_code, 200)
        self.assertIn("metadataBlocks", response.json)


    def test_empty_metadata_codemeta_create(self):
        response = self.client.get('/metadata/codemeta20?method=create')
        self.assertEqual(response.status_code, 200)
        self.assertIn("datasetVersion", response.json)

        
