from . import Translate
from . import MergeTranslator
from . import AdditionTranslator
from . import Translator
from . import Rules


class Config(object):
    ''' Gets a config file and creates translators. '''

    def __init__(self):
        ''' Constructor '''
        pass
                   
    @staticmethod        
    def create(self, translator_yaml, source_format):   
        """ returns a translator object out of the yaml mapping """
        
        if (source_format_ == 'text'):     
            source_key = translator_yaml.get('source_key',None) 
            target_key = translator_yaml.get('target_key',None)
            priority = translator_yaml.get('priority',None) 
            translator_type = translator_yaml.get('type',None)
            join_symbol = translator_yaml.get('join_symbol',None)
            class_name = translator_yaml.get('class',None)    
            
            if (len(translator_yaml) == 1):                # case 1: copy translator
                source_key = target_key
                translator = Translate.Translate(source_key, target_key, priority)   
            if (len(translator_yaml) == 2):                # case 2: normal translator
                translator = Translate.Translate(source_key, target_key, priority)         
            if("type" in translator_yaml):                               
                if(translator_yaml["type"] == "addition"):# case 3: addition translator
                    translator = AdditionTranslator.AdditionTranslator(source_key, target_key, class_name, translator_type, priority)              
                if(translator_yaml["type"] == "merge"):   # case 4: merge translator                         
                    translator = MergeTranslator.MergeTranslator(source_key, target_key, translator_type, join_symbol, priority)
                if(translator_yaml["type"] == "rule"):    # case 5: rules
                    trigger = source_key
                    translator = Rules.Rules(trigger, translator_yaml, priority)
        return translator
        
        
        
        
        