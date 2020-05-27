import yaml
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
    rules = TranslatorFactory.create_rules(rules)            
    
    # Return config Object for MAPPINGS dictionary.
    config = Config(scheme, description, format, translators, rules)        
    return config                # global variable for the rules dictionary
        


def read_all_config_files():
    # for file in resources/config:
    rootdir = './resources/config'

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            path = os.path.join(subdir, file)
            open_yaml_file = open(path)            
            config = read_config(open_yaml_file)
            MAPPINGS[file.name] = config
      

def read_all_tsv_files():
    #for file in resources/tsv
    # mb = read_tsv(file)
    # DV_CONFIG[mb.name] = mb
    pass
    
        
def read_tsv(data):
    # metadataBlock = MetadataBlock(dict_with_data)
    # return metadataBlock    
    pass