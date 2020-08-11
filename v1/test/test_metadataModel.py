import unittest
import sys
sys.path.append('..')

from models.MetadataModel import PrimitiveFieldScheme, PrimitiveField
from models.MetadataModel import MultiplePrimitiveFieldScheme
from models.MetadataModel import MultiplePrimitiveField
from models.MetadataModel import CompoundFieldScheme, CompoundField
from models.MetadataModel import MultipleCompoundFieldScheme
from models.MetadataModel import MultipleCompoundField
from models.MetadataModel import EditFormat, EditScheme
# from models.MetadataModel import SimpleFieldSchema, FieldsScheme, EditScheme, MetadataBlockSchema, DatasetSchema, CreateDatasetSchema


class TestMetadataModel(unittest.TestCase):
    def setUp(self):
        self.simple_data = {'typeName': 'testfeld', 'value': 'simpleValue'}
        self.multiple_simple_data = {'typeName': 'multipleTest',
                                     'value': [
                                         'simpleData1',
                                         'simpleData2',
                                         'simpleData3']}
        self.compound_data = {'typeName': 'testcompound',
                              'value':
                                  {'a': 'valueA', 'b': 'valueB'}}
        self.multiple_compound_data = {'typeName': 'testcompound',
                                       'value': [
                                            {'a': 'valueA1', 'b': 'valueB1'},
                                            {'a': 'valueA2', 'b': 'valueB2'},
                                            {'a': 'valueA3', 'b': 'valueB3'}]}
        pass

    def test_primitiveField(self):
        p_field = PrimitiveField(
            self.simple_data['typeName'],
            self.simple_data['value'])
        self.assertEqual(p_field.get_multiple(), False)
        self.assertEqual(p_field.get_typeClass(), 'primitive')
        result = PrimitiveFieldScheme().dump(p_field)
        # print(result)
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

    def test_multipleCompoundField(self):
        mc_field = MultipleCompoundField(self.multiple_compound_data['typeName'])




    def test_editScheme(self):

        edit = EditFormat()
    
        p_field = PrimitiveField(
            self.simple_data['typeName'],
            self.simple_data['value'])
        edit.add_field(p_field)

        p_field2 = PrimitiveField(
            'title',
            'Das ist ein Testtitel für einen Datensatz'
        )

        edit.add_field(p_field2)

        c_field = CompoundField(
            'author'
        )
        p_field3 = PrimitiveField(
            'authorName',
            'Dorothea Iglezakis'
        )
        p_affiliation = PrimitiveField(
            'authorAffiliation',
            'Universität Stuttgart'
        )
        c_field.add_value(p_field3, 'authorName')
        c_field.add_value(p_affiliation, 'authorAffiliation')

        edit.add_field(c_field)

        result = EditScheme().dump(edit)
        print (result)
            
