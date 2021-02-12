import yaml
import csv
import os
from models.Config import Config
from models.Field import Field
from models.TranslatorFactory import TranslatorFactory
from models.Translator import Translator
TranslatorFactory = TranslatorFactory()
from api.globals import MAPPINGS, DV_FIELD, DV_CHILDREN, DV_MB, SOURCE_KEYS      #global variables

# Read config yaml files (mapping from source key to target keys)
def read_all_config_files():  
    rootdir = './resources/config'
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            path = os.path.join(subdir, file)
            open_yaml_file = open(path)            
            config = read_config(open_yaml_file)    
            scheme = file.split(".")[0]    
            # fill global dictionary of mappings
            MAPPINGS[scheme] = config
            open_yaml_file.close()

# Read schema tsv files (metadatablocks nesting)      
def read_all_tsv_files():
    rootdir = './resources/tsv'
        
    # for file in resources/resources
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            path = os.path.join(subdir, file)
            open_tsv_file = open(path)            
            read_tsv(open_tsv_file)
            open_tsv_file.close()


def read_config(data):
    yaml_file = yaml.safe_load(data) 
    # Extracting dictionaries out of yaml-file    
    scheme = yaml_file["scheme"]   
    description = yaml_file["description"]
    format = yaml_file["format"]   
    mapping = yaml_file["mapping"]
    rules = yaml_file["rules"]
    
    # Return rules dictionary for trigger source keys (key) and associated translators (value).        
    # rules_dict = TranslatorFactory.create_rules(rules)  
    
    config = Config(scheme, description, format) 
                                          
    # Create dict of translators out of the mapping    
    for translator_yaml in mapping:
        config.add_translator(translator_yaml)
    
    # Create dict of Rules out of the mapping
    for rule_yaml in rules:
        config.add_rules(rule_yaml)       
        
    # Return config Object for MAPPINGS dictionary           
    return config               
   

def read_tsv(data):
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