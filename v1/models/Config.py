from models.TranslatorFactory import TranslatorFactory
from models.Translator import BaseTranslator, MergeTranslator, AdditionTranslator
import pyaml

class Config(object):
    ''' object after parsing a mapping file '''

    def __init__(self, scheme, description, format, yaml_file):
        ''' Constructor '''
        self.scheme = scheme
        self.description = description
        self.format = format
        self.translators_dict = {}
        self.rules_dict = {}
        self.target_keys = []
        self.addition_translators_dict = {}
        self.source_keys = []
        self.namespaces = {}
        self.yaml_file = yaml_file

    def __repr__(self):
        return("scheme: " + self.scheme + ", description: " + self.description + ", format: " + self.format + ", translators: " + str(self.translators_dict) + ", rules dict: " + str(self.rules_dict))
       
    def pretty_yaml(self):
        return pyaml.dump(self.yaml_file)
    
    def get_translator(self, source_key):
        return self.translators_dict.get(source_key)

    def dump(self):
        return {"scheme": self.scheme, "description": self.description, "format": self.format}
    
    def get_source_keys(self):
        return self.source_keys
    
    def get_target_keys(self):
        self.target_keys = list(dict.fromkeys(self.target_keys))
        return self.target_keys
    
    # create dictionary with source key (keys) and translators (value)
    def add_translator(self, translator_yaml):
        translator = TranslatorFactory.create_translator(translator_yaml) 
        source_key = translator.get_source_key()
        target_key = translator.get_target_key()
        self.target_keys.append(target_key)
        if isinstance(translator, AdditionTranslator):      # special case: addition translators
            self.addition_translators_dict[source_key] = translator  
        else:
            if type(source_key) == list:    # special case: merge translators
                for key in source_key:
                    self.source_keys.append(key)
                    self.translators_dict[key] = translator
            else:
                self.translators_dict[source_key] = translator
                self.source_keys.append(source_key)
        
    def add_rules(self, rule_yaml):
        # siehe Translator Factory
        t = {}        # initialize inner translator dictionary
        trigger = rule_yaml.get("trigger", None)
        self.source_keys.append(trigger)
        trigger_values = rule_yaml.get("trigger_values", None)
        for trigger_value in trigger_values:
            translators_yaml = rule_yaml.get(trigger_value, None)   # get list of translators for trigger value: [{source_key: description, targetKey: seriesInformation}]
            translators = []                                        # intitialize list of translators for translator_dict
            for translator in translators_yaml:
                source_key = translator.get('source_key', None)
                self.source_keys.append(source_key)
                target_key = translator.get('target_key', None)
                translators.append(BaseTranslator(source_key, target_key))
            t[trigger_value] = translators            # fill inner dictionary with trigger_value and list_of_translators
            
            self.rules_dict[trigger] = t
            
    def add_namespace(self, name_space):
        # transform string to dict
        namespace_split = name_space.split("=", 1)
        self.namespaces[namespace_split[0]]=namespace_split[1]
        
        