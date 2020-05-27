from models.Translator import Translator

class TranslatorFactory(object):
    ''' Gets a config file and creates translators. '''

    def __init__(self):
        ''' Constructor '''
        pass
                
                   
    @staticmethod      
    def create_translator(translator_yaml, format):   
        """ returns a translator object out of the yaml mapping """
        
        if (format == 'text/plain'):     
            source_key = translator_yaml.get('source_key',None) 
            target_key = translator_yaml.get('target_key',None)
            priority = translator_yaml.get('priority',None) 
            translator_type = translator_yaml.get('type',None)
            join_symbol = translator_yaml.get('join_symbol',None)
            class_name = translator_yaml.get('class',None)    
            
            if (len(translator_yaml) == 1):                # case 1: copy translator
                source_key = target_key
                translator = Translator.Base_Translator(source_key, target_key, priority)   
            if (len(translator_yaml) == 2):                # case 2: normal translator
                translator = Translator.Base_Translator(source_key, target_key, priority)         
            if("type" in translator_yaml):                               
                if(translator_yaml["type"] == "addition"):# case 3: addition translator
                    translator = Translator.AdditionTranslator(source_key, target_key, class_name, translator_type, priority)              
                if(translator_yaml["type"] == "merge"):   # case 4: merge translator                         
                    translator = Translator.MergeTranslator(source_key, target_key, translator_type, join_symbol, priority)
        return translator
    
    
    @staticmethod
    def create_rules(self, rules_yaml):
        """ 
        returns nested rules dictionary
        rules_dict = {'contact_role': {'producer': list_of_translators, 'distributor': list_of_translators},
                      'description.descriptionType': {'SeriesInformation': list_of_translators},
                      ...
                      trigger: {trigger_value: list_of_translators}
                     }         
        """        
        rules_dict = {}
        for rule_yaml in rules_yaml:
            translator_dict = {}                                                # initialize inner dictionary
            trigger = rule_yaml.get('source_key', None)
            trigger_values = rule_yaml.get('trigger_values', None)                    
            
            for trigger_value in trigger_values:
                list_of_translators_yaml = rule_yaml.get(trigger_value, None)   # get list of translators for trigger value: [{source_key: description, targetKey: seriesInformation}]
                list_of_translators = []                                        # intitialize list of translators for translator_dict
                for translator in list_of_translators_yaml:
                    source_key = translator.get('source_key', None)
                    target_key = translator.get('target_key', None)
                    list_of_translators.append(Translate.Translate(source_key, target_key))
                translator_dict[trigger_value] = list_of_translators            # fill inner dictionary with trigger_value and list_of_translators
            
            rules_dict[trigger] = translator_dict                               # fill outer dictionary with trigger and inner dictionary
            
        return rules_dict
        
        
        
        