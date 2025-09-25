import json
import unittest
import sys
sys.path.append('..')

from api.app import create_app


class TestZenodoMetadata(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        
    def test_zenodoOutput(self):
        with (open(r'test/input/testmetadata-citation.json', 'rb') as f):
            file_content = f.read()
            jsonFile = json.loads(file_content)
            response = self.client.post('/metadata/zenodo?method=edit', data=json.dumps(jsonFile),
                                        headers={'Content-Type':'application/json'})
            self.assertEqual(response.status_code, 200)
            with open(r'test/output/zenodo_output.json', 'rb') as file:
                file_output_content = file.read()
                jsonReturnObjectAPI = json.loads(response.data.decode('utf-8'))
                jsonReturnObjectFile = json.loads(file_output_content.decode('utf-8'))
                self.assertEqual(jsonReturnObjectAPI,jsonReturnObjectFile)
        
    def test_zenodoDifficultJSONInput(self):
        with (open(r'test/input/testmetadata-citation-diff.json', 'rb') as f):
            file_content = f.read()
            jsonFile = json.loads(file_content)
            response = self.client.post('/metadata/zenodo?method=edit', data=json.dumps(jsonFile),
                                        headers={'Content-Type':'application/json'})
            self.assertEqual(response.status_code, 200)
            with open(r'test/output/zenodo_output.json', 'rb') as file:
                file_output_content = file.read()
                jsonReturnObjectAPI = json.loads(response.data.decode('utf-8'))
                jsonReturnObjectFile = json.loads(file_output_content.decode('utf-8'))
                self.assertEqual(jsonReturnObjectAPI,jsonReturnObjectFile)

    def test_zenodoJSONInput(self):
        with (open(r'test/input/correct_target_key.json', 'rb') as f):
            file_content = f.read()
            jsonFile = json.loads(file_content)
            response = self.client.post('/metadata/zenodo?method=edit', data=json.dumps(jsonFile),
                                        headers={'Content-Type':'application/json'})
            self.assertEqual(response.status_code, 200)
            with open(r'test/output/zenodo_output2.json', 'rb') as file:
                file_output_content = file.read()
                jsonReturnObjectAPI = json.loads(response.data.decode('utf-8'))
                jsonReturnObjectFile = json.loads(file_output_content.decode('utf-8'))
                self.assertEqual(jsonReturnObjectAPI,jsonReturnObjectFile)

    def test_zenodoWRONGJSONInput(self):
        with (open(r'test/input/wrong_target_key.json', 'rb') as f):
            file_content = f.read()
            jsonFile = json.loads(file_content)
            response = self.client.post('/metadata/zenodo?method=edit', data=json.dumps(jsonFile),
                                        headers={'Content-Type':'application/json'})
            self.assertEqual(response.status_code, 400)
            with open(r'test/output/zenodo_output_fail.txt', 'rb') as file:
                file_output_content = file.read()
                jsonReturnObjectAPI = json.loads(response.data.decode('utf-8'))
                jsonReturnObjectFile = file_output_content.decode('utf-8')
                self.assertEqual(jsonReturnObjectAPI["message"],jsonReturnObjectFile)