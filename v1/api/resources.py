import yaml
import csv
import os
from models.Config import Config
from models.Field import Field
from models.TranslatorFactory import TranslatorFactory
TranslatorFactory = TranslatorFactory()
from api.globals import MAPPINGS, DV_FIELD, DV_CHILDREN, DV_MB



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
            print(MAPPINGS)

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
    
    start_metadata_block = False
    start_schema = False
    start_vocabulary = False    
    for row in tsv_file:
        
        # save index of tsv dynamically
        counter_column = 0
        for column in row:
            # target_key fields starting
            if (column == "#datasetField"):
                start_schema = True
                continue
            # controlled_vocabulary fields starting
            if (column == "#controlledVocabulary"):
                start_vocabulary = True
                start_schema = False
                continue
            if (column == "#metadataBlock"):
                column_metadataBlock = counter_column
                start_metadata_block = True
                continue  
            if (column == "allowmultiples"):
                column_multiples = counter_column
            if (column == "metadatablock_id"):
                colum_metadatablock = counter_column
            if (column == "fieldType"):
                column_fieldtype = counter_column
            if (column == "name"):
                column_targetkey = counter_column
            if (column == "displayName"):
                column_displayname = counter_column
            if(column == "parent"):
                column_parent = counter_column
            if (column == "allowControlledVocabulary"):
                column_controlledVocabulary = counter_column
            if (column == "Value"):
                column_valuecontrolledVocabulary = counter_column 
            counter_column += 1
                                  
        if (start_metadata_block):
            DV_MB[row[column_targetkey]]=row[column_displayname]
            start_metadata_block = False
            continue
                    
        if (start_schema):        
            multiple = row[column_multiples]
            parent = row[column_parent]
            target_key = row[column_targetkey]            
            if(parent == ""):
                parent = None
            
            # check type_class
            type_class = "primitive"
            metadata_block = row[column_metadataBlock]
            if(row[column_fieldtype] == "none"):
                type_class = "compound"      
                DV_CHILDREN[target_key] = []      
            if(row[column_controlledVocabulary] == "TRUE"):
                type_class = "controlled_vocabulary"
            
            # create parent/children map
            if parent in DV_CHILDREN:
                DV_CHILDREN[parent].append(target_key)
                
            field = Field(multiple, type_class, parent, metadata_block)             
            DV_FIELD[target_key] = field 
                
        if(start_vocabulary):
            field = DV_FIELD[row[column_controlledVocabulary]]
            field.set_controlled_vocabulary(row[column_valuecontrolledVocabulary])
    print(DV_FIELD)

   