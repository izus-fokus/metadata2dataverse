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
from api.globals import MAPPINGS, DV_FIELD, DV_CHILDREN, DV_MB, SOURCE_KEYS      #global variables


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
    rootdir = './resources/tsv'        
    # for file in resources/resources
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            path = os.path.join(subdir, file)
            open_tsv_file = open(path)            
            read_scheme(open_tsv_file)
            open_tsv_file.close()


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
                abort(409, scheme + " with format " + mapping.format)
                break
        MAPPINGS[scheme].append(config)
    else: 
        MAPPINGS[scheme] = [config]    
          

def read_scheme(data):
    """ Parses all information from scheme, and saves information to the global dictionaries 
        DV_FIELD, DV_CHILDREN, and DV_MB.         
        
    Parameters
    ---------
    data : opened tsv file    
    """    
    tsv_file = csv.reader(data, delimiter="\t")    
    start_metadata_block = False
    start_schema = False
    start_vocabulary = False    
    for row in tsv_file:      
        if not all('' == s or s.isspace() for s in row):
            if(row[0] == "#datasetField"):            
                try:
                    index_targetkey = row.index("name")
                    index_multiple = row.index("allowmultiples")
                    index_metadatablock = row.index("metadatablock_id")
                    index_fieldtype = row.index("fieldType")
                    index_parent = row.index("parent")
                    index_hascontrolledvoc = row.index("allowControlledVocabulary")
                except ValueError:
                    print("Check TSV #datasetField column names. Should contain name, allowmultiples, metadatablock_id, fieldType, parent and allowControlledVocabulary.")
                start_schema = True
                continue        
            if(row[0] == "#controlledVocabulary"):
                try:
                    index_valuecontrolledvoc = row.index("Value")
                except ValueError:
                        print("Check TSV #controlledVocabulary column names. Should contain Value.")
                start_vocabulary = True
                start_schema = False
                continue        
            if(row[0] == "#metadataBlock"):
                try:
                    index_mbname = row.index("name")
                    index_displayname = row.index("displayName")
                except ValueError:
                    print("Check TSV #metadataBlock column names. Should contain displayName.")
                start_metadata_block = True  
                continue                                  
            if (start_metadata_block):
                DV_MB[row[index_mbname]]=row[index_displayname]
                start_metadata_block = False
                continue                    
            if (start_schema):        
                multiple = row[index_multiple]
                parent = row[index_parent]
                target_key = row[index_targetkey]            
                if(parent == ""):
                    parent = None            
                # check type (primitive, compound, controlled vocabulary)
                type_class = "primitive"
                metadata_block = row[index_metadatablock]
                if(row[index_fieldtype] == "none"):
                    type_class = "compound"      
                    DV_CHILDREN[target_key] = []      
                if(row[index_hascontrolledvoc] == "TRUE"):
                    type_class = "controlled_vocabulary"            
                # create parent/children map
                if parent in DV_CHILDREN:
                    DV_CHILDREN[parent].append(target_key)                
                field = Field(target_key, multiple, type_class, parent, metadata_block)             
                DV_FIELD[target_key] = field                 
            if(start_vocabulary):
                field = DV_FIELD[row[index_targetkey]]
                field.set_controlled_vocabulary(row[index_valuecontrolledvoc])