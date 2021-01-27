import unittest
import sys
sys.path.append('..')

from api.app import create_app


class TestMetadataMapperEndpoints(unittest.TestCase):
    def setUp(self):
        self.__init__()
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    def test_empty_metadata(self):

        response = self.client.get('/metadata/harvester')
        self.assertEqual(response.status_code, 200)

    def test_get_mappings(self):
        response = self.client.get("/mapping")
        self.assertEqual(response.status_code, 200)