from abc import abstractstaticmethod, ABCMeta

class Translator(metaclass=ABCMeta):
    """ Factory-Class """

    def get_source_key():
        """ Translator Interface """ 
        
        
class BaseTranslator(Translator):    

    def __init__(self, source_key, target_key, priority = 1):        
        self.source_key = source_key
        self.target_key = target_key 
        self.priority = priority 
    
    def __repr__(self):
        return ("source key: " + str(self.source_key) + ", target key: " + str(self.target_key))
        
    def get_source_key(self):
        return self.source_key
    
    
        
class AdditionTranslator(BaseTranslator):    
    def __init__(self, class_name, translator_type="addition",  *args, **kwargs):
        super(AdditionTranslator, self).__init__(*args, **kwargs)
        self.class_name = class_name
        self.translator_type = translator_type
    
    def __repr__(self):
        return ("source key: " + self.source_key + ", target key: " + self.target_key)
    
    def get_source_key(self):
        return self.source_key
        
        
class MergeTranslator(BaseTranslator):
    
    def __init__(self, translator_type = "merge", join_symbol = " ", *args, **kwargs):
        super(MergeTranslator, self).__init__(*args, **kwargs)
        self.translator_type = translator_type
        self.join_symbol = join_symbol
        
    def __repr__(self):
        return ("source key: " + str(self.source_key) + ", target key: " + str(self.target_key))
        
    def get_source_key(self):
        return self.source_key