import yaml
import csv
import os
import pyaml
from models.Config import Config
from models.Field import Field
from models.TranslatorFactory import TranslatorFactory
from models.Translator import Translator
from builtins import isinstance
from flask import abort, g
TranslatorFactory = TranslatorFactory()
from api.globals import MAPPINGS, DV_FIELD, DV_CHILDREN, DV_MB, SOURCE_KEYS, CREDENTIALS_PATH    #global variables
import requests
import json
import logging
logging.basicConfig(level=logging.INFO)


def read_all_config_files(): 
    """ Opens all config files located in './resources/config'  and gives them to read_config() method.
    
    If config file has no errors, it is transferred to fill_MAPPINGS() method. 
    Otherwise abort with file errors.    
    """    
    g.warnings = []
    rootdir = './resources/config'
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            path = os.path.join(subdir, file)
            open_yaml_file = open(path)            
            config = read_config(open_yaml_file)
            open_yaml_file.close()
            # check if yaml file was correct    
            if len(g.warnings) > 0:
                warnings = ' '.join(g.warnings)
                abort(500, warnings)            
            fill_MAPPINGS(config)
            

# Read schema tsv files (metadatablocks nesting)      
def read_all_scheme_files():
    """ Opens all schemes from './resources/tsv' and gives them to read_scheme() method. """    
    with open(CREDENTIALS_PATH,"r") as cred_file:
        credentials = json.load(cred_file)
        dataverse_url = credentials["base_url"]
    try:
        read_scheme_from_api(dataverse_url + "api/metadatablocks/")
    except Exception as e:
        print (f"Error while loading metadata schemata: {e}")
    # rootdir = './resources/tsv'      
    # for file in resources/resources
    # for subdir, dirs, files in os.walk(rootdir):
    #     for file in files:
    #         path = os.path.join(subdir, file)
    #         open_tsv_file = open(path, encoding="utf-8")
    #         read_scheme(open_tsv_file)
    #         open_tsv_file.close()


def read_config(data):    
    """ Parses all information from config file, returns config object.
    
    Parameters
    ------------
    data : opened yaml file
    
    Returns
    ------------
    config : Config obj    
    """    
    g.warnings = []
    yaml_file = yaml.safe_load(data)     
    # check for missing content
    content_list = ["scheme", "description", "format", "mapping"]
    for content in content_list:
        if content not in yaml_file:
            g.warnings.append("{} missing in YAML file {}.".format(content, data))    
    if len(g.warnings) > 0:
        return None        
    # Extracting dictionaries out of yaml-file   
    scheme = yaml_file["scheme"]   
    description = yaml_file["description"]
    format = yaml_file["format"]   
    mapping = yaml_file["mapping"]
    config = Config(scheme, description, format, yaml_file)                                               
    # Create dict of translators out of the mapping    
    for translator_yaml in mapping:
        config.add_translator(translator_yaml)  
    # Create dict of Rules
    if "rules" in yaml_file:
        rules = yaml_file["rules"]      
        for rule_yaml in rules:
            config.add_rules(rule_yaml)                  
    # Create dict of namespaces
    if "namespaces" in yaml_file: 
        namespaces = yaml_file["namespaces"]       
        if isinstance(namespaces,list):     # more than one namespace
            for namespace in namespaces:
                config.add_namespace(namespace)
        else:
            config.add_namespace(namespaces) # one namespace                       
    return config    
   
def fill_MAPPINGS(config):
    """ Fills global MAPPINGS dictionary with config object.
    
    Checks format of config file if scheme already exists. If format already exists: Abortion.
    
    Parameters
    ---------
    config : obj      
    """
    
    # fill global dictionary of mappings
    scheme = config.scheme
    if scheme in MAPPINGS:
        # check if mapping-format already exists
        for mapping in MAPPINGS[scheme]:
            if mapping.format == config.format:
                g.warnings.append(scheme + " with format " + mapping.format + " already existing")
            else:
                MAPPINGS[scheme].append(config)
    else: 
        MAPPINGS[scheme] = [config]    
          

# def read_scheme(data):
""" This function has been replaced by read_scheme_from_api"""
#     """ Parses all information from scheme, and saves information to the global dictionaries 
#         DV_FIELD, DV_CHILDREN, and DV_MB.         
        
#     Parameters
#     ---------
#     data : opened tsv file    
#     """    
#     tsv_file = csv.reader(data, delimiter="\t")    
#     start_metadata_block = False
#     start_schema = False
#     start_vocabulary = False    
#     for row in tsv_file:      
#         if not all('' == s or s.isspace() for s in row):
#             row = [elem.strip() for elem in row]
#             if(row[0] == "#datasetField"):            
#                 try:
#                     index_targetkey = row.index("name")
#                     index_multiple = row.index("allowmultiples")
#                     index_metadatablock = row.index("metadatablock_id")
#                     index_fieldtype = row.index("fieldType")
#                     index_parent = row.index("parent")
#                     index_hascontrolledvoc = row.index("allowControlledVocabulary")
#                 except ValueError as e:
#                     print(row)
#                     print("Check TSV #datasetField column names. Should contain name, allowmultiples, metadatablock_id, fieldType, parent and allowControlledVocabulary.")
#                     print(e)
#                 start_schema = True
#                 continue        
#             if(row[0] == "#controlledVocabulary"):
#                 try:
#                     index_valuecontrolledvoc = row.index("Value")
#                 except ValueError:
#                         print("Check TSV #controlledVocabulary column names. Should contain Value.")
#                 start_vocabulary = True
#                 start_schema = False
#                 continue        
#             if(row[0] == "#metadataBlock"):
#                 try:
#                     index_mbname = row.index("name")
#                     index_displayname = row.index("displayName")
#                 except ValueError:
#                     print("Check TSV #metadataBlock column names. Should contain displayName.")
#                 start_metadata_block = True  
#                 continue                                  
#             if (start_metadata_block):
#                 DV_MB[row[index_mbname]]=row[index_displayname]
#                 start_metadata_block = False
#                 continue                    
#             if (start_schema):        
#                 multiple = row[index_multiple]
#                 parent = row[index_parent]
#                 target_key = row[index_targetkey]            
#                 if(parent == ""):
#                     parent = None            
#                 # check type (primitive, compound, controlled vocabulary)
#                 type_class = "primitive"
#                 metadata_block = row[index_metadatablock]
#                 field_type = row[index_fieldtype]
#                 if(row[index_fieldtype] == "none"):
#                     type_class = "compound"      
#                     DV_CHILDREN[target_key] = []      
#                 if(row[index_hascontrolledvoc] == "TRUE"):
#                     type_class = "controlled_vocabulary"            
#                 # create parent/children map
#                 if parent in DV_CHILDREN:
#                     DV_CHILDREN[parent].append(target_key)                
#                 field = Field(target_key, multiple, type_class, parent, metadata_block, field_type)             
#                 DV_FIELD[target_key] = field                 
#             if(start_vocabulary):
#                 field = DV_FIELD[row[index_targetkey]]
#                 field.set_controlled_vocabulary(row[index_valuecontrolledvoc])

def get_field_object(field, block_name, parent=None):
    target_key = field['name']
    multiple = "TRUE" if field.get('multiple') else "FALSE"
    type_class = field.get('typeClass', 'primitive')
    metadata_block = block_name
    field_type = field['type']
    has_controlled_vocab = field.get('isControlledVocabulary', False)

    # Create the Field object and store it in DV_FIELD
    field_obj = Field(target_key, multiple, type_class, parent, metadata_block, field_type)

    # Handle controlled vocabulary
    if has_controlled_vocab:
        vocab_values = field.get('controlledVocabularyValues', [])
        field_obj.set_controlled_vocabulary(vocab_values)

    return field_obj




def read_scheme_from_api(base_url):
    """
    Fetches metadata information from a Dataverse instance and saves information 
    to the global dictionaries DV_FIELD, DV_CHILDREN, and DV_MB.

    Parameters
    ---------
    base_url : str
        The base URL for the Dataverse API (e.g., "https://demo.dataverse.org/api/metadatablocks/")
    """
    # Fetch the list of metadata blocks
    response = requests.get(base_url)
    response.raise_for_status()
    metadata_blocks = response.json().get('data', [])

    for block in metadata_blocks:
        block_name = block['name']
        block_display_name = block['displayName']
        DV_MB[block_name] = block_display_name

        # Fetch metadata block details
        block_url = f"{base_url}/{block_name}"
        block_response = requests.get(block_url)
        block_response.raise_for_status()
        block_details = block_response.json().get('data', {})
        # logging.info("DV_MB2: {}".format(DV_MB2))

        fields = block_details.get('fields', {})
        for field_name, field in fields.items():
            field_obj = get_field_object(field, block_name)

            # Handle child fields if the field is of type compound
            if field_obj.get_type_class() == "compound":
                child_fields = field.get('childFields', {})
                parent_name = field_obj.get_name()
                for child_name, child_field in child_fields.items():
                    child_obj = get_field_object(child_field, block_name, parent_name)
                    # Add child field to the parent field's child_fields
                    field_obj.add_child(child_name, child_obj)

                    # Store the child field in DV_FIELD
                    DV_FIELD[child_name] = child_obj
                    # Update the parent-child relationship in DV_CHILDREN
                    if field_obj.get_name() not in DV_CHILDREN:
                        DV_CHILDREN[parent_name] = []
                    if child_name not in DV_CHILDREN[parent_name]:
                        DV_CHILDREN[parent_name].append(child_name)
            # child fields nicht doppelt
            if not field_obj.get_name() in DV_FIELD:
                DV_FIELD[field_obj.get_name()] = field_obj
