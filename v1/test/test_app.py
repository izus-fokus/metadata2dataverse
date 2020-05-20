import unittest
import json
import sys
sys.path.append('..')

from api.app import create_app

class TestMetadataMapperEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_edit_metadata(self):
        response = self.client.post('/metadata/test')
        self.assertEqual(response.status_code, 200)
