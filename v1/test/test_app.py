import unittest
import sys
sys.path.append('..')

from api.app import create_app


class TestMetadataMapperEndpoints(unittest.TestCase):
    def setUp(self):
        #self.__init__()
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    def test_post_harvester_data(self):
        # testen der priorities
        with open(r'./input/priority_test.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)      
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'author', 'value': [{'authorName': {'type': 'PrimitiveField', 'typeName': 'authorName', 'value': 'Dorothea Iglezakis'}}]}]})
        
        # testen des Configtypes merge: 1. Einfacher Merge mit Symbol ";"
        with open(r'./input/merge_test1.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)    
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'dsDescription', 'value': [{'dsDescriptionValue': {'type': 'PrimitiveField', 'typeName': 'dsDescriptionValue', 'value': 'Abstract; Dies ist die Abstract Description!'}}]}]})
        
        # testen des Configtypes merge: 2. dreifacher Merge (engMetaGitterPoints)
        #with open(r'./input/merge_test2.txt', 'rb') as f:
        #    file_content = f.read()
        #response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        #self.assertEqual(response.status_code, 200)    
        #self.assertEqual(response.json, {'fields': [{'type': 'CompoundField', 'typeName': 'engMetaTemp', 'value': {'engMetaTempPoints': {'type': 'PrimitiveField', 'typeName': 'engMetaTempPoints', 'value': '1; 2; 3'}}}]})
        
        # testen des Configtypes merge: 3. Merge mit mehreren Values (authorName)
        with open(r'./input/merge_test3.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)    
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'author', 'value': [{'authorName': {'type': 'PrimitiveField', 'typeName': 'authorName', 'value': 'Anne Kreuter'}}, {'authorName': {'type': 'PrimitiveField', 'typeName': 'authorName', 'value': 'Dorothea Iglezakis'}}]}]})
        
        # testen multiplecompoundfields mit Kindern die unterschiedliche Felder besetzen
        with open(r'./input/unterschiedliche_felder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'datasetContact', 'value': [{'datasetContactName': {'type': 'PrimitiveField', 'typeName': 'datasetContactName', 'value': 'Dorothea Iglezakis'}, 'datasetContactAffiliation':{'type': 'PrimitiveField', 'typeName': 'datasetContactAffiliation', 'value': 'Uni Stuttgart'}}, {'datasetContactName': {'type': 'PrimitiveField', 'typeName': 'datasetContactName', 'value': 'Anett Seeland'}, 'datasetContactAffiliation':{'type': 'PrimitiveField', 'typeName': 'datasetContactAffiliation', 'value': 'IZUS'}}, {'datasetContactName': {'type': 'PrimitiveField', 'typeName': 'datasetContactName', 'value': 'Max Mustermann'}}]}]})
        
        # testen des Configtypes: addition
        with open(r'./input/adder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json, {'fields': [{'type': 'PrimitiveField', 'typeName': 'title', 'value': 'Test titel'},{'type': 'PrimitiveField', 'typeName': 'dateOfDeposit', 'value': '2021/02/12'}]})
        
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
        
        
        
    def test_empty_metadata(self):
        response = self.client.get('/metadata/harvester')
        self.assertEqual(response.status_code, 200)

    def test_get_mappings(self):
        response = self.client.get('/mapping')
        self.assertEqual(response.status_code, 200)