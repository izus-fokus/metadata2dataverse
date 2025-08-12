import unittest
from unittest.mock import patch, MagicMock
import requests

# Assume these are your global dictionaries to be populated
DV_MB = {}
DV_FIELD = {}
DV_CHILDREN = {}

# Dummy Field class (to be used within the code)
class Field:
    def __init__(self, target_key, multiple, type_class, parent, metadata_block, field_type):
        self.target_key = target_key
        self.multiple = multiple
        self.type_class = type_class
        self.parent = parent
        self.metadata_block = metadata_block
        self.field_type = field_type
        self.controlled_vocabulary = []
        self.child_fields = {}

# This is your function
def read_scheme_from_api(base_url):
    response = requests.get(base_url)
    response.raise_for_status()
    metadata_blocks = response.json().get('data', [])
    
    for block in metadata_blocks:
        block_name = block['name']
        block_display_name = block['displayName']
        DV_MB[block_name] = block_display_name

        block_url = f"{base_url}/{block_name}"
        block_response = requests.get(block_url)
        block_response.raise_for_status()
        block_details = block_response.json().get('data', {})
        fields = block_details.get('fieldsElement', {})
        
        for field_name, field in fields.items():
            target_key = field['name']
            multiple = field.get('multiple', False)  # Assuming default is False
            type_class = field.get('typeClass', 'primitive')
            parent = field.get('parent', None)
            metadata_block = block_name
            field_type = field['type']
            has_controlled_vocab = field.get('isControlledVocabulary', False)

            # Create the Field object and store it in DV_FIELD
            field_obj = Field(target_key, multiple, type_class, parent, metadata_block, field_type)
            DV_FIELD[target_key] = field_obj

            # Handle controlled vocabulary
            if has_controlled_vocab:
                vocab_values = field.get('controlledVocabularyValues', [])
                field_obj.controlled_vocabulary.extend(vocab_values)

            # If the field has a parent, update DV_CHILDREN
            if parent:
                if parent not in DV_CHILDREN:
                    DV_CHILDREN[parent] = []
                DV_CHILDREN[parent].append(target_key)

            # Handle child fieldsElement if the field is of type compound
            if type_class == "compound":
                child_fields = field.get('childFields', {})
                for child_name, child_field in child_fields.items():
                    child_obj = Field(
                        target_key=child_field['name'],
                        multiple=child_field.get('multiple', False),
                        type_class=child_field.get('typeClass', 'primitive'),
                        parent=target_key,
                        metadata_block=metadata_block,
                        field_type=child_field['type']
                    )
                    field_obj.child_fields[child_name] = child_obj
                    DV_FIELD[child_name] = child_obj
                    if target_key not in DV_CHILDREN:
                        DV_CHILDREN[target_key] = []
                    DV_CHILDREN[target_key].append(child_name)

class TestReadSchemeFromAPI(unittest.TestCase):

    @patch('requests.get')
    def test_read_scheme_from_api(self, mock_get):
        # Mock the response for metadata blocks
        mock_metadata_blocks_response = {
            'data': [
                {'name': 'block1', 'displayName': 'Block 1'},
                {'name': 'block2', 'displayName': 'Block 2'}
            ]
        }

        # Mock the detailed block response for block1
        mock_block1_response = {
            'data': {
                'fieldsElement': {
                    'field1': {
                        'name': 'field1',
                        'multiple': True,
                        'typeClass': 'primitive',
                        'type': 'TEXT',
                        'isControlledVocabulary': False,
                        'parent': None
                    }
                }
            }
        }

        # Mock the detailed block response for block2
        mock_block2_response = {
            'data': {
                'fieldsElement': {
                    'field2': {
                        'name': 'field2',
                        'multiple': False,
                        'typeClass': 'compound',
                        'type': 'TEXT',
                        'isControlledVocabulary': True,
                        'controlledVocabularyValues': ['Value1', 'Value2'],
                        'parent': None,
                        'childFields': {
                            'childField1': {
                                'name': 'childField1',
                                'multiple': False,
                                'typeClass': 'primitive',
                                'type': 'TEXT'
                            }
                        }
                    }
                }
            }
        }

        # Configure the mock_get side effect to return different responses for each call
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: mock_metadata_blocks_response),  # First call
            MagicMock(status_code=200, json=lambda: mock_block1_response),           # Second call
            MagicMock(status_code=200, json=lambda: mock_block2_response)            # Third call
        ]

        # Call the function with a mock base URL
        base_url = "https://demo.dataverse.org/api/metadatablocks"
        read_scheme_from_api(base_url)

        # Assertions for DV_MB dictionary
        self.assertEqual(DV_MB['block1'], 'Block 1')
        self.assertEqual(DV_MB['block2'], 'Block 2')

        # Assertions for DV_FIELD dictionary
        field1_obj = DV_FIELD['field1']
        self.assertEqual(field1_obj.target_key, 'field1')
        self.assertEqual(field1_obj.multiple, True)
        self.assertEqual(field1_obj.type_class, 'primitive')
        self.assertEqual(field1_obj.field_type, 'TEXT')

        field2_obj = DV_FIELD['field2']
        self.assertEqual(field2_obj.target_key, 'field2')
        self.assertEqual(field2_obj.multiple, False)
        self.assertEqual(field2_obj.type_class, 'compound')
        self.assertEqual(field2_obj.field_type, 'TEXT')
        self.assertEqual(field2_obj.controlled_vocabulary, ['Value1', 'Value2'])

        # Assertions for child fieldsElement
        child_field1_obj = field2_obj.child_fields['childField1']
        self.assertEqual(child_field1_obj.target_key, 'childField1')
        self.assertEqual(child_field1_obj.multiple, False)

        # Assertions for DV_CHILDREN dictionary
        self.assertIn('field2', DV_CHILDREN)
        self.assertIn('childField1', DV_CHILDREN['field2'])

if __name__ == '__main__':
    unittest.main()
