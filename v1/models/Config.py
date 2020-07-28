from models.TranslatorFactory import TranslatorFactory
from models.Translator import BaseTranslator, MergeTranslator, AdditionTranslator

class Config(object):
    ''' object after parsing a mapping file '''

    def __init__(self, scheme, description, format):
        ''' Constructor '''
        self.scheme = scheme
        self.description = description
        self.format = format
        self.translators_dict = {}
        self.rules_dict = {}

    def __repr__(self):
        return("scheme: " + self.scheme + ", description: " + self.description + ", format: " + self.format + ", translators: " + str(self.translators_dict) + ", rules dict: " + str(self.rules_dict))
    
    def get_translator(self, source_key):
        return self.translators_dict.get(source_key)
    
    def get_source_keys(self):
        return translators_dict.keys()
    
    # create dictionary with source key (keys) and translators (value)
    def add_translator(self, translator_yaml):
        translator = TranslatorFactory.create_translator(translator_yaml) 
        source_key = translator.get_source_key()
        if type(source_key) == list:    # special case: merge translators
            for key in source_key:
                self.translators_dict[key] = translator
        else:
            self.translators_dict[source_key] = translator
        
    def add_rules(self, rule_yaml):
        # siehe Translator Factory
        t = {}        # initialize inner translator dictionary
        trigger = rule_yaml.get("trigger", None)
        trigger_values = rule_yaml.get("trigger_values", None)
        for trigger_value in trigger_values:
            translators_yaml = rule_yaml.get(trigger_value, None)   # get list of translators for trigger value: [{source_key: description, targetKey: seriesInformation}]
            translators = []                                        # intitialize list of translators for translator_dict
            for translator in translators_yaml:
                source_key = translator.get('source_key', None)
                target_key = translator.get('target_key', None)
                translators.append(BaseTranslator(source_key, target_key))
            t[trigger_value] = translators            # fill inner dictionary with trigger_value and list_of_translators
            
            self.rules_dict[trigger] = t