import unittest
import sys
sys.path.append('..')

from api.app import create_app


class TestEndpointGetEmpty(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        
    def test_getSchemeMapping(self):
        response = self.client.get('/mapping/harvester?formatSetting=plain/txt')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/mapping/engmeta?formatSetting=text/xml')
        self.assertEqual(response.status_code, 200)


        response = self.client.get('/mapping/codemeta20')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/mapping/blubb')
        self.assertEqual(response.status_code, 404)


    def test_createSchemeMapping(self):
        with open(r'test/input/new_mapping.yaml', 'rb') as f:
            file_content = f.read()
            response = self.client.post('/mapping', data=file_content, headers={'Content-Type':'application/yaml'})
            response = self.client.get('/mapping/engmeta?formatSetting=diesdas')
            self.assertEqual(response.status_code, 200)
        
    def test_deditSchemaMapping(self):
        with open(r'test/input/new_mapping.yaml', 'rb') as f:
            file_content = f.read()
            response = self.client.put('/mapping/engpeta', data=file_content, headers={'Content-Type':'application/yaml'})
            self.assertEqual(response.status_code, 404)
            response = self.client.put('/mapping/engmeta?formatSetting=somethingelse', data=file_content, headers={'Content-Type':'application/yaml'})
            self.assertEqual(response.status_code, 400)
            response = self.client.put('/mapping/engmeta?formatSetting=diesdas', data=file_content, headers={'Content-Type':'application/yaml'})
            self.assertEqual(response.status_code, 204)
            response = self.client.put('/mapping/engmeta', data=file_content, headers={'Content-Type':'application/yaml'})
            self.assertEqual(response.status_code, 204)

        
                                   
    def test_deleteSchemeMapping(self):
        response = self.client.delete('/mapping/engmeta?formatSetting=diesdas')
        self.assertEqual(response.status_code, 204)
        
        response = self.client.delete('/mapping/blubb')
        self.assertEqual(response.status_code, 404)
        
        response = self.client.delete('/mapping/engmeta?formatSetting=blub')
        self.assertEqual(response.status_code, 400)
