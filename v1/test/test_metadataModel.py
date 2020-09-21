import unittest
import sys
sys.path.append('..')

from models.MetadataModel import PrimitiveFieldScheme, PrimitiveField, MultiplePrimitiveField, MultiplePrimitiveFieldScheme
from models.MetadataModel import CompoundFieldScheme, CompoundField, MultipleCompoundField, MultipleCompoundFieldScheme
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
        result = MultiplePrimitiveFieldScheme(only=['value', 'typeName']).dump(p_field)
        self.assertIn('value', result)
        self.assertIn('typeName', result)
        self.assertNotIn('multiple', result)
        self.assertNotIn('typeClass', result)
        
    def test_multipleCompoundField(self):
        pass


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
