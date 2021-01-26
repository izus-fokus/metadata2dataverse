import unittest
import json
import sys
sys.path.append('..')

from api.app import create_app
from api.globals import MAPPINGS


class TestMetadataMapperEndpoints(unittest.TestCase):
    def setUp(self):
        self.__init__()
        self.app = create_app()
        print(self.app)
        self.client = self.app.test_client()

    def test_edit_metadata(self):
        response = self.client.post('/metadata/harvester')
        self.assertEqual(response.status_code, 200)
