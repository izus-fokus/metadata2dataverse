import yaml
from models.Config import Config

def read_config(data):
    yaml_file = yaml.safe_load(data)    
    
    description = yaml_file["description"]
    scheme = yaml_file["scheme"]   
    format = yaml_file["format"]          
    mapping = yaml_file["mapping"]
    rules = yaml_file["rules"]  
                                    
    translators = []                                    # create list of unfilled translators out of mapping
    for translator_yaml in mapping:
        translator_list.append(TranslatorFactory.create_translator(translator_yaml, format))
            
    rules_dict = TranslatorFactory.create_rules(rules)            
    
    config = Config(scheme, description, format, translators, rules_dict)        
    return config                # global variable for the rules dictionary
        


def read_all_config_files():
    # for file in resources/config:
    # config = read_config(read(file))    
    # MAPPINGS[config.name] = config
    # go through all files in resources/config
    pass
    

def read_all_tsv_files():
    #for file in resources/tsv
    # mb = read_tsv(file)
    # DV_CONFIG[mb.name] = mb
    pass
    
        
def read_tsv(data):
    # metadataBlock = MetadataBlock(dict_with_data)
    # return metadataBlock    
    pass