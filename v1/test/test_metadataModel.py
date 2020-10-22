import unittest
import sys
sys.path.append('..')

from models.MetadataModel import PrimitiveFieldScheme, PrimitiveField
from models.MetadataModel import MultiplePrimitiveFieldScheme
from models.MetadataModel import MultiplePrimitiveField
from models.MetadataModel import CompoundFieldScheme, CompoundField
from models.MetadataModel import MultipleCompoundFieldScheme
from models.MetadataModel import MultipleCompoundField
from models.MetadataModel import EditFormat, EditScheme, EditFieldSchema
from models.MetadataModel import Field, FieldSchema
from models.MetadataModel import MetadataBlock, MetadataBlockSchema
# from models.MetadataModel import SimpleFieldSchema, FieldsScheme, EditScheme, MetadataBlockSchema, DatasetSchema, CreateDatasetSchema


class TestMetadataModel(unittest.TestCase):
    def setUp(self):
        self.primitive_data = {'typeName': 'title', 'value': 'New Post Publish'}
        self.multiple_data = {'typeName': 'language', 'value': ['German', 'English']}

        self.compound_parent = {'typeName': 'engMetaGitter'}
        self.compound_child1 = {'typeName': 'engMetaGitterCountX', 'value': '60'}
        self.compound_child2 = {'typeName': 'engMetaGitterCountY', 'value': '80'}

        self.multiple_compound_parent = {'typeName': 'author'}        
        self.multiple_compound_child1 = {'typeName': 'authorName', 'value': ['Elisabeth', 'Anne']}
        self.multiple_compound_child2 = {'typeName': 'authorCity', 'value': ['Büdingen', 'Stuttgart']}

    def test_primitiveField(self):
        p_field = PrimitiveField(
            self.primitive_data['typeName'],
            self.primitive_data['value'])
        self.assertEqual(p_field.get_multiple(), False)
        self.assertEqual(p_field.get_typeClass(), 'primitive')
        result = PrimitiveFieldScheme().dump(p_field)
        self.assertEqual(result['typeName'], self.primitive_data['typeName'])
        self.assertEqual(result['value'], self.primitive_data['value'])
        self.assertEqual(result['typeClass'], 'primitive')
        self.assertFalse(result['multiple'])
        result = PrimitiveFieldScheme(only=['value', 'typeName']).dump(p_field)
        self.assertIn('value', result)
        self.assertIn('typeName', result)
        self.assertNotIn('multiple', result)
        self.assertNotIn('typeClass', result)
        self.assertNotIn('type', result)

    def test_multiplePrimitiveField(self):
        p_field = MultiplePrimitiveField(
            self.multiple_data['typeName'],
            self.multiple_data['value'])
        self.assertEqual(p_field.get_multiple(), True)
        self.assertEqual(p_field.get_typeClass(), 'primitive')
        result = MultiplePrimitiveFieldScheme().dump(p_field)
        self.assertEqual(result['typeName'], self.multiple_data['typeName'])
        self.assertEqual(result['value'], self.multiple_data['value'])
        self.assertEqual(result['typeClass'], 'primitive')
        self.assertTrue(result['multiple'])
        self.assertNotIn('type', result)
        result = MultiplePrimitiveFieldScheme(only=['value', 'typeName']).dump(p_field)
        self.assertIn('value', result)
        self.assertIn('typeName', result)
        self.assertNotIn('multiple', result)
        self.assertNotIn('typeClass', result)
        
    def test_multipleCompoundField(self):
        c_field = MultipleCompoundField(
            self.multiple_compound_parent['typeName']
        )
        self.assertEqual(c_field.get_multiple(), True)
        self.assertEqual(c_field.get_typeClass(), 'compound')
        s1_field = MultiplePrimitiveField(
            self.multiple_compound_child1['typeName'],
            self.multiple_compound_child1['value']
        )
        s2_field = MultiplePrimitiveField(
            self.multiple_compound_child2['typeName'],
            self.multiple_compound_child2['value']
        )
        self.assertEqual(s1_field.get_multiple(), True)
        self.assertEqual(s2_field.get_typeClass(), 'primitive')
        # for i in range(len(self.multiple_compound_child1['value'])):            
        c_field.add_value(s1_field)
        c_field.add_value(s2_field)
        result = MultipleCompoundFieldScheme().dump(c_field)
        self.assertIn('value', result)
        # self.assertIn(self.multiple_compound_child1['typeName'], result['value'])
        # self.assertIn(self.multiple_compound_child2['typeName'], result['value'])


    def test_compoundField(self):
        c_field = CompoundField(
            self.compound_parent['typeName']
        )
        self.assertEqual(c_field.get_multiple(), False)
        self.assertEqual(c_field.get_typeClass(), 'compound')
        s1_field = PrimitiveField(
            self.compound_child1['typeName'],
            self.compound_child1['value']
        )
        s2_field = PrimitiveField(
            self.compound_child2['typeName'],
            self.compound_child2['value']
        )
        c_field.add_value(s1_field, self.compound_child1['typeName'])
        c_field.add_value(s2_field, self.compound_child2['typeName'])
        result = CompoundFieldScheme().dump(c_field)
        self.assertIn('value', result)
        self.assertIn(self.compound_child1['typeName'], result['value'])
        self.assertIn(self.compound_child2['typeName'], result['value'])

    def test_editScheme(self):

        edit = EditFormat()
        p_field = PrimitiveField(
            self.primitive_data['typeName'],
            self.primitive_data['value'])
        edit.add_field(p_field)

        c2_field = MultipleCompoundField(
            'author'
        )
        
        c3_field = CompoundField('author')

        p_field3 = PrimitiveField(
            'authorName',
            'Dorothea Iglezakis'
        )
        p_affiliation = PrimitiveField(
            'authorAffiliation',
            'Universität Stuttgart'
        )
        c3_field.add_value(p_field3, 'authorName')
        c3_field.add_value(p_affiliation, 'authorAffiliation')
        
        c2_field.add_value(c3_field)
        edit.add_field(c2_field)
        result = EditScheme().dump(edit)
        print(result)
        self.assertEqual(len(result["fields"]), 2)
        for field in result["fields"]:
            self.assertIn('typeName', field)
            self.assertIn('value', field)
            self.assertNotIn('type', field)
            self.assertNotIn('multiple', field)
            self.assertNotIn('typeClass', field)

    def test_metadatablock(self):
        id = 'citation'
        displayName = 'Citation'
        mb = MetadataBlock(id,displayName)
        result = MetadataBlockSchema().dump(mb)
        self.assertEqual(result['displayName'], displayName)
        self.assertEqual(result['id'], id)
        
