import unittest
import sys
sys.path.append('..')

from models.MetadataModel import PrimitiveFieldScheme, PrimitiveField
from models.MetadataModel import CompoundFieldScheme, CompoundField
# from models.MetadataModel import SimpleFieldSchema, FieldsScheme, EditScheme, MetadataBlockSchema, DatasetSchema, CreateDatasetSchema


class TestMetadataModel(unittest.TestCase):
    def setUp(self):
        self.simple_data = {'typeName': 'testfeld', 'value': 'simpleValue'}
        pass

    def test_primitiveField(self):
        p_field = PrimitiveField(
            self.simple_data['typeName'],
            self.simple_data['value'])
        self.assertEqual(p_field.get_multiple(), False)
        self.assertEqual(p_field.get_typeClass(), 'primitive')
        result = PrimitiveFieldScheme().dump(p_field)
        self.assertEqual(result['typeName'], self.simple_data['typeName'])
        self.assertEqual(result['value'], self.simple_data['value'])
        self.assertEqual(result['typeClass'], 'primitive')
        self.assertFalse(result['multiple'])
        result = PrimitiveFieldScheme(only=['value', 'typeName']).dump(p_field)
        self.assertIn('value', result)
        self.assertIn('typeName', result)
        self.assertNotIn('multiple', result)
        self.assertNotIn('typeClass', result)

    def test_compoundField(self):
        c_field = CompoundField(
            self.simple_data['typeName']
        )
        self.assertEqual(c_field.get_multiple(), False)
        self.assertEqual(c_field.get_typeClass(), 'compound')
        s_field = PrimitiveField(
            self.simple_data['typeName'],
            self.simple_data['value']
        )
        c_field.add_value(s_field, 'test1')
        c_field.add_value(s_field, 'test2')
        result = CompoundFieldScheme().dump(c_field)
        self.assertIn('value', result)
        self.assertIn('test1', result['value'])
        self.assertIn('test2', result['value'])
