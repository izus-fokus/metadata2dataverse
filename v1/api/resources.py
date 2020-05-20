import yaml
from models.Config import Config

def read_config(data):
    data = yaml.safe_load(data)    
    mapping = data["mapping"]   
    source_format = data["format"]                          # e.g. "text"
    translator_list = []
    for translator_yaml in mapping:
        translator_list.append(Config.create(translator_yaml, source_format))
       
    dict_mappings[source_format] = translator_list          # global variable


def read_all_config_files():
    # for file in resources/config:
    #    config = read_config(read(file))
    
    # MAPPINGS[config.name] = config
    # go through all files in resources/config
    # 

def read_tsv(data):

    #metadataBlock = MetadataBlock(dict_with_data)
    #return metadataBlock

def read_all_tsv_files():
    #for file in resources/tsv
    # mb = read_tsv(file)
    # DV_CONFIG[mb.name] = mb