import unittest
import json
import sys
sys.path.append('..')

from api.app import create_app
from api.globals import MAPPINGS, DV_FIELD, DV_MB, DV_CHILDREN


class TestMetadataMapperEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()


    def test_empty_metadata(self):

        response = self.client.get('/metadata/harvester')
        self.assertEqual(response.status_code, 200)

    def test_get_mappings(self):
        response = self.client.get("/mapping")
        self.assertEqual(response.status_code, 200)