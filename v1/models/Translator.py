'''
Created on 17.03.2020

@author: annekreuter
'''
from abc import abstractstaticmethod, ABCMeta

class Translator(metaclass=ABCMeta):
    """ Factory-Class """

    def getSourceKey():
        """ Translator Interface """ 
        
        
class Base_Translator(Translator):    

    def __init__(self, source_key, target_key, priority = 1):        
        self.source_key = source_key
        self.target_key = target_key 
        self.priority = priority 
        
    def getSourceKey(self):
        return self.source_key
    
        
class AdditionTranslator(Base_Translator):
    
    def __init__(self, class_name, translator_type="addition",  *args, **kwargs):
        super(AdditionTranslator, self).__init__(*args, **kwargs)
        self.class_name = class_name
        self.translator_type = translator_type
    
    def getSourceKey(self):
        return self.source_key
        
        
class MergeTranslator(Base_Translator):
    
    def __init__(self, translator_type = "merge", join_symbol = " ", *args, **kwargs):
        super(AdditionTranslator, self).__init__(*args, **kwargs)
        self.translator_type = translator_type
        self.join_symbol = join_symbol
        
    def getSourceKey(self):
        return self.source_key