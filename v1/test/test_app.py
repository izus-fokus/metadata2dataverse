import unittest
import sys
sys.path.append('..')
import requests
import json

from api.app import create_app


class TestMetadataMapperEndpoints(unittest.TestCase):
    def setUp(self):
        #self.__init__()
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.headers = {'X-Dataverse-key': '0f72c986-defc-486b-afe7-d4524d7d3c17'}
        
    def test_post_engmeta_data(self):
        with open(r'./input/EngMeta_example_v0.2.xml', 'rb') as f:
            file_content = f.open()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'text/xml'})
        self.assertEqual(response.status_code, 200)  
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)
        

    def test_post_harvester_data(self):
        # testen der priorities        
        with open(r'./input/priority_test.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'author', 'value': [{'authorName': {'type': 'PrimitiveField', 'typeName': 'authorName', 'value': 'Selent'}}]}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)        
        
        # testen des Configtypes merge: 1. Einfacher Merge mit Symbol ";"
        with open(r'./input/merge_test1.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'dsDescription', 'value': [{'dsDescriptionValue': {'type': 'PrimitiveField', 'typeName': 'dsDescriptionValue', 'value': 'Abstract; Dies ist die Abstract Description!'}}]}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)
        
        # testen des Configtypes merge: 2. dreifacher Merge (engMetaTempPoints)
        # dataverse bug: compoundfield wirft 500 Fehler
        with open(r'./input/merge_test2.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)    
        self.assertEqual(response.json, {'fields': [{'type': 'CompoundField', 'typeName': 'engMetaTemp', 'value': {'engMetaTempPoints': {'type': 'PrimitiveField', 'typeName': 'engMetaTempPoints', 'value': '1; 2; 3'}}}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 500)
        
        # testen des Configtypes merge: 3. Merge mit mehreren Values (authorName)
        with open(r'./input/merge_test3.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)   
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'author', 'value': [{'authorName': {'type': 'PrimitiveField', 'typeName': 'authorName', 'value': 'Anne Kreuter'}}, {'authorName': {'type': 'PrimitiveField', 'typeName': 'authorName', 'value': 'Dorothea Iglezakis'}}]}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)
        
        # testen multiplecompoundfields mit Kindern die unterschiedliche Felder besetzen
        # dataverse: contact email is required -> sollte auch der metadataMapper wissen?
        with open(r'./input/unterschiedliche_felder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'datasetContact', 'value': [{'datasetContactName': {'type': 'PrimitiveField', 'typeName': 'datasetContactName', 'value': 'Dorothea Iglezakis'}, 'datasetContactAffiliation':{'type': 'PrimitiveField', 'typeName': 'datasetContactAffiliation', 'value': 'Uni Stuttgart'}}, {'datasetContactName': {'type': 'PrimitiveField', 'typeName': 'datasetContactName', 'value': 'Anett Seeland'}, 'datasetContactAffiliation':{'type': 'PrimitiveField', 'typeName': 'datasetContactAffiliation', 'value': 'IZUS'}}, {'datasetContactName': {'type': 'PrimitiveField', 'typeName': 'datasetContactName', 'value': 'Max Mustermann'}}]}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        print(x.text)
        self.assertEqual(x.status_code, 403)
        
        # testen des Configtypes: addition
        with open(r'./input/adder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json, {'fields': [{'type': 'PrimitiveField', 'typeName': 'title', 'value': 'Test titel'},{'type': 'PrimitiveField', 'typeName': 'dateOfDeposit', 'value': '2021-05-31'}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)
        
        # schema existiert nicht
        with open(r'./input/adder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harwäster?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 404) 
        
        # content-type existiert nicht
        with open(r'./input/adder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/text'})
        self.assertEqual(response.status_code, 404) 
        
        # source key existiert nicht
        with open(r'./input/unknown_key.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 202) 
        self.assertEqual(response.json, {'fields': [{'type': 'PrimitiveField', 'typeName': 'title', 'value': 'Test titel'},{'type': 'PrimitiveField', 'typeName': 'dateOfDeposit', 'value': '2021-05-31'}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)
                
        # input key has multiple values but is primitive field
        with open(r'./input/single_multiple.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 202) 
        self.assertEqual(response.json, {'fields': [{'type': 'PrimitiveField', 'typeName': 'title', 'value': 'Test title 1'},{'type': 'PrimitiveField', 'typeName': 'dateOfDeposit', 'value': '2021-05-31'}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)
        
        # rule 1
        # dataverse bug: compoundfield wirft 500 Fehler
        with open(r'./input/rule.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json, {'fields': [{'type': 'CompoundField', 'typeName': 'series', 'value': {'seriesInformation': {'type': 'PrimitiveField', 'typeName': 'seriesInformation', 'value': 'Hallo geht das hier?'}}}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 500)
        
        # rule 2
        with open(r'./input/rule2.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'producer', 'value': [{'producerName': {'type': 'PrimitiveField', 'typeName': 'producerName', 'value': 'Anett Seeland'},'producerAffiliation': {'type': 'PrimitiveField', 'typeName': 'producerAffiliation', 'value': 'Uni Stuttgart'},'producerAbbreviation': {'type': 'PrimitiveField', 'typeName': 'producerAbbreviation', 'value': 'FoKUS'}}]}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)
        
        # controlledVocabulary with wrong value
        with open(r'./input/controlled_voc.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 202) 
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleVocabularyField', 'typeName': 'language', 'value': ['German', 'Danish']}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json), headers=self.headers)
        self.assertEqual(x.status_code, 200)
        
        response = self.client.post('/metadata/harvester?method=edit&verbose=True', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 202)
        self.assertIn('warnings', response.json)
        self.assertEqual(response.json['response'], {'fields': [{'type': 'MultipleVocabularyField', 'typeName': 'language', 'value': ['German', 'Danish']}]})
        x = requests.put("https://demodarus.izus.uni-stuttgart.de/api/datasets/:persistentId/editMetadata?persistentId=doi:10.15770/darus-510&replace=true", data=json.dumps(response.json['response']), headers=self.headers)
        self.assertEqual(x.status_code, 200)
                
        
        
    def test_empty_metadata(self):
        pass
        #response = self.client.get('/metadata/harvester')
        #self.assertEqual(response.status_code, 200)

    def test_get_mappings(self):
        pass
        #response = self.client.get('/mapping')
        #self.assertEqual(response.status_code, 200)
        