import unittest
import sys
import requests
import json
from lxml import etree as ET
from datetime import date, datetime

sys.path.append('..')
from api.app import create_app


class TestMetadataMapperEndpoints(unittest.TestCase):
    def setUp(self):
        #self.__init__()
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        now = date.today()
        self.actual_date = now.strftime("%Y-%m-%d")

        with open("./input/credentials.json","r") as cred_file:
            credentials = json.load(cred_file)
            self.headers = {'X-Dataverse-key': credentials["api_key"]}
            self.dataverse_url = credentials["base_url"]
            self.dataset = credentials["dataset_id"]

    def test_post_engmeta_data(self):
        with open(r'./input/EngMeta_example_v0.2.xml', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/engmeta?method=edit&verbose=True', data=file_content, headers={'Content-Type':'text/xml'})
        self.assertEqual(response.status_code, 202)
        self.assertIn("warnings",response.json)

        response = self.client.post('/metadata/engmeta?method=edit', data=file_content, headers={'Content-Type':'text/xml'})
        self.assertEqual(response.status_code, 200)
        url = "{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset)
        x = requests.put(
            url,
            data=json.dumps(response.json),
            headers=self.headers)
        self.assertEqual(x.status_code, 200)



    def test_post_harvester_data(self):
        # testen der priorities
        with open(r'./input/priority_test.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'author', 'value': [{'authorName': {'typeName': 'authorName', 'value': 'Selent'}}]}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)

        # testen des Configtypes merge: 1. Einfacher Merge mit Symbol ";"
        with open(r'./input/merge_test1.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'dsDescription', 'value': [{'dsDescriptionValue': {'typeName': 'dsDescriptionValue', 'value': 'Abstract; Dies ist die Abstract Description!'}}]}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)

        # testen des Configtypes merge: 2. dreifacher Merge (engMetaTempPoints)
        # dataverse bug: compoundfield wirft 500 Fehler
        with open(r'./input/merge_test2.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'engMetaTemp', 'value': {'engMetaTempPoints': {'typeName': 'engMetaTempPoints', 'value': '1; 2; 3'}}}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 400)

        # testen des Configtypes merge: 3. Merge mit mehreren Values (authorName)
        with open(r'./input/merge_test3.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'author', 'value': [{'authorName': {'typeName': 'authorName', 'value': 'Anne Kreuter'}}, {'authorName': {'typeName': 'authorName', 'value': 'Dorothea Iglezakis'}}]}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)

        # testen multiplecompoundfields mit Kindern die unterschiedliche Felder besetzen
        # dataverse: contact email is required -> sollte auch der metadataMapper wissen?
        with open(r'./input/unterschiedliche_felder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'datasetContact', 'value': [{'datasetContactName': {'typeName': 'datasetContactName', 'value': 'Dorothea Iglezakis'}, 'datasetContactAffiliation':{'typeName': 'datasetContactAffiliation', 'value': 'Uni Stuttgart'}}, {'datasetContactName': {'typeName': 'datasetContactName', 'value': 'Anett Seeland'}, 'datasetContactAffiliation':{'typeName': 'datasetContactAffiliation', 'value': 'IZUS'}}, {'datasetContactName': {'typeName': 'datasetContactName', 'value': 'Max Mustermann'}}]}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 403)

        # testen des Configtypes: addition
        with open(r'./input/adder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'title', 'value': 'Test titel'},{'typeName': 'dateOfDeposit', 'value': self.actual_date}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)

        # schema existiert nicht
        with open(r'./input/adder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harväster?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 404)

        # content-type existiert nicht
        with open(r'./input/adder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/text'})
        self.assertEqual(response.status_code, 400)

        # source key existiert nicht
        with open(r'./input/unknown_key.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'title', 'value': 'Test titel'},{'typeName': 'dateOfDeposit', 'value': self.actual_date}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)

        # input key has multiple values but is primitive field
        with open(r'./input/single_multiple.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'title', 'value': 'Test title 1'},{'typeName': 'dateOfDeposit', 'value': self.actual_date}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)

        # rule 1
        # dataverse bug: compoundfield wirft 500 Fehler
        with open(r'./input/rule.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'series', 'value': {'seriesInformation': {'typeName': 'seriesInformation', 'value': 'Hallo geht das hier?'}}}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 400)

        # rule 2
        with open(r'./input/rule2.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'producer', 'value': [{'producerName': {'typeName': 'producerName', 'value': 'Anett Seeland'},'producerAffiliation': {'typeName': 'producerAffiliation', 'value': 'Uni Stuttgart'},'producerAbbreviation': {'typeName': 'producerAbbreviation', 'value': 'FoKUS'}}]}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)

        # controlledVocabulary with wrong value
        with open(r'./input/controlled_voc.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'typeName': 'language', 'value': ['German', 'Danish']}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)

        response = self.client.post('/metadata/harvester?method=edit&verbose=True', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 202)
        self.assertIn('warnings', response.json)
        self.assertEqual(response.json['response'], {'fields': [{'typeName': 'language', 'value': ['German', 'Danish']}]})
        x = requests.put("{}/api/datasets/:persistentId/editMetadata?persistentId={}&replace=true".format(self.dataverse_url, self.dataset), data=json.dumps(response.json['response']), headers=self.headers)
        self.assertEqual(x.status_code, 200)

        with open(r'./input/test_jsonld_reader.jsonld', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/m4i?method=edit', data=file_content, headers={'Content-Type':'application/jsonld'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/metadata/m4i?method=edit&verbose=True', data=file_content, headers={'Content-Type':'application/jsonld'})
        self.assertEqual(response.status_code, 202)
        print("JSONLD TESTS DONE")
        self.assertIn('warnings', response.json)

        with open(r'./input/opendihu_example.jsonld', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/m4i?method=edit', data=file_content, headers={'Content-Type':'application/jsonld'})
        #print("response:",response)
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/metadata/m4i?method=edit&verbose=True', data=file_content, headers={'Content-Type':'application/jsonld'})
        self.assertEqual(response.status_code, 202)
        print("JSONLD TESTS DONE")
        self.assertIn('warnings', response.json)
