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
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'author', 'value': [{'authorName': {'type': 'PrimitiveField', 'typeName': 'authorName', 'value': 'Dorothea Iglezakis'}},{'authorName': {'type': 'PrimitiveField', 'typeName': 'authorName', 'value': 'Anne Kreuter'}}]}]})
        
        # testen der merges (1. Unterschiedliche Mergesymbols (dsDescriptionValue), 2. dreifacher Merge (engMetaGitterPoints), 3. Merge mit mehreren Values (authorName)
        with open(r'./input/merge_tests.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)    
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'dsDescription', 'value': [{'dsDescriptionValue': {'type': 'PrimitiveField', 'typeName': 'dsDescriptionValue', 'value': 'Abstract; Dies ist die Abstract Description!'}}]},{'type': 'MultipleCompoundField', 'typeName': 'author', 'value': [{'authorName': {'type': 'PrimitiveField', 'typeName': 'authorName', 'value': 'Dorothea Iglezakis'}},{'authorName': {'type': 'PrimitiveField', 'typeName': 'authorName', 'value': 'Anne Kreuter'}}]}]})
        
        # testen multiplecompoundfields mit Kindern die unterschiedliche Felder besetzen
        with open(r'./input/unterschiedliche_felder.txt', 'rb') as f:
            file_content = f.read()
        response = self.client.post('/metadata/harvester?method=edit', data=file_content, headers={'Content-Type':'plain/txt'})
        self.assertEqual(response.status_code, 200)     
        print(response.json) 
        self.assertEqual(response.json, {'fields': [{'type': 'MultipleCompoundField', 'typeName': 'datasetContact', 'value': [{'datasetContactName': {'type': 'PrimitiveField', 'typeName': 'datasetContactName', 'value': 'Dorothea Iglezakis'}, 'datasetContactAffiliation':{'type': 'PrimitiveField', 'typeName': 'datasetContactAffiliation', 'value': 'Uni Stuttgart'}}, {'datasetContactName': {'type': 'PrimitiveField', 'typeName': 'datasetContactName', 'value': 'Anett Seeland'}, 'datasetContactAffiliation':{'type': 'PrimitiveField', 'typeName': 'datasetContactAffiliation', 'value': 'IZUS'}}, {'datasetContactName': {'type': 'PrimitiveField', 'typeName': 'datasetContactName', 'value': 'Max Mustermann'}}]}]})
        
        
        
    def test_empty_metadata(self):
        response = self.client.get('/metadata/harvester')
        self.assertEqual(response.status_code, 200)

    def test_get_mappings(self):
        response = self.client.get('/mapping')
        self.assertEqual(response.status_code, 200)