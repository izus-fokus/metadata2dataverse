from abc import abstractstaticmethod, ABCMeta

class Translator(metaclass=ABCMeta):
    """ Factory-Class """

    def get_source_key():
        """ Translator Interface """ 
    def set_value():
        """ Translator Interface """ 
    def get_target_key():
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
    
    def get_target_key(self):
        return self.target_key
    
    def set_value(self, values):
        self.value = values
    
    
        
class AdditionTranslator(Translator):    
    def __init__(self, source_key, target_key, class_name, translator_type = "addition", priority = 1):
        self.source_key = source_key
        self.target_key = target_key 
        self.priority = priority
        self.class_name = class_name
        self.translator_type = translator_type
    
    def __repr__(self):
        return ("source key\: " + self.source_key + "\, target key\: " + self.target_key)
    
    def get_source_key(self):
        return self.source_key
    
    def get_target_key(self):
        return self.target_key
    
    def set_value(self, values):
        self.value = values
        
        
class MergeTranslator(Translator):
    
    def __init__(self, source_key, target_key, priority = 1, translator_type = "merge", join_symbol = " "):
        self.source_key = source_key
        self.target_key = target_key 
        self.priority = priority
        self.translator_type = translator_type
        self.join_symbol = join_symbol
        
    def __repr__(self):
        return ("source key\: " + str(self.source_key) + ", target key: " + str(self.target_key))
        
    def get_source_key(self):
        return self.source_key
    
    def get_target_key(self):
        return self.target_key
    
    def set_value(self, values):
        self.value = values