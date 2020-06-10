import yaml
import csv
import os
from models.Config import Config
from models.TranslatorFactory import TranslatorFactory
TranslatorFactory = TranslatorFactory()

def read_config(data):
    yaml_file = yaml.safe_load(data) 
    
    # Extracting dictionaries out of yaml-file.
    description = yaml_file["description"]
    scheme = yaml_file["scheme"]   
    format = yaml_file["format"]   
    mapping = yaml_file["mapping"]
    rules = yaml_file["rules"]
                        
    # Create list of unfilled translators out of the mapping.                                
    translators = []            
    for translator_yaml in mapping:
        translators.append(TranslatorFactory.create_translator(translator_yaml, format))
            
    # Return rules dictionary for trigger source keys (key) and associated translators (value).        
    rules_dict = TranslatorFactory.create_rules(rules)            
    
    # Return config Object for MAPPINGS dictionary.
    config = Config(scheme, description, format, translators, rules_dict)        
    return config                # global variable for the rules dictionary
        


def read_all_config_files():  
    rootdir = './resources/config'
        
    # for file in resources/config
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            path = os.path.join(subdir, file)
            open_yaml_file = open(path)            
            config = read_config(open_yaml_file)
            # fill global dictionary of mappings
            MAPPINGS[file] = config
      

def read_all_tsv_files():
    rootdir = './resources/tsv'
        
    # for file in resources/resources
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            path = os.path.join(subdir, file)
            open_tsv_file = open(path)            
            config = read_tsv(open_tsv_file)
    
        
def read_tsv(data):
    tsv_file = csv.reader(data, delimiter="\t")
    for field in tsv_file:
        # target_key fields starting
        if (row[0] == "#datasetField"):
            start_schema = True
            continue
        
        # controlled_vocabulary fields starting            
        if (row[0] == "#controlledVocabulary"):
            start_vocabulary = True
            start_schema = False
            continue
        
        # reading display_name and save it in DV_MB
        if (row[0] == "#metadataBlock"):
            start_metadata_block = True
            continue                    
        if (start_metadata_block):
            DV_MB[row[1]]=row[3]
            start_metadata_block = False
            continue
                    
        if (start_schema):        
            multiple = row[10]
            parent = row[14]
            target_key = row[1]            
            if(parent == ""):
                parent = none
            
            # check type_class
            type_class = "primitive"
            metadata_block = row[15]
            if(field[5] == "none"):
                type_class = "compound"      
                DV_CHILDREN[target_key] = [None]      
            if(field[9] == "TRUE"):
                type_class = "controlled_vocabulary"
            
            # create parent/children map
            if parent in DV_CHILDREN:
                DV_CHILDREN[parent].append(target_key)
                
            field = Field(multiple, typeClass, parent, metadata_block)             
            DV_FIELD[target_key] = field 
                
        if(start_vocabulary):
            field = DV_FIELD[row[1]]
            field.set_controlled_vocabulary(row[2])