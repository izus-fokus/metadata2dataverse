from abc import abstractstaticmethod, ABCMeta
from models.DateAdder import DateAdder

class Translator(metaclass=ABCMeta):
    """ Factory-Class """

    def get_source_key():
        """ Translator Interface """ 
    def get_target_key():
        """ Translator Interface """ 
    def get_value():
        """ Translator Interface """ 
    def get_priority():
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
        
    def get_value(self,source_key_values):
        v = source_key_values.get(self.source_key)                        
        return v
    
    def get_priority(self):
        return self.priority
    
    
        
class AdditionTranslator(Translator):    
    def __init__(self, source_key, target_key, class_name, translator_type = "addition", priority = 1):
        self.source_key = source_key
        self.target_key = target_key 
        self.priority = priority
        self.class_name = class_name
        self.translator_type = translator_type
    
    def __repr__(self):
        return ("source key: " + self.source_key + ", target key: " + self.target_key)
    
    def get_translator_type(self):    
        return self.translator_type
    
    def get_source_key(self):
        return self.source_key
    
    def get_target_key(self):
        return self.target_key
    
    def get_value(self):
        klass = globals()[self.class_name]
        value = klass().main()
        return value
        
        
        
class MergeTranslator(Translator):    
    def __init__(self, source_keys, target_key, priority = 1, translator_type = "merge", merge_symbol = " "):
        self.source_keys = source_keys
        self.target_key = target_key 
        self.priority = priority
        self.translator_type = translator_type
        self.merge_symbol = merge_symbol
        
    def __repr__(self):
        return ("source keys: " + str(self.source_keys) + ", target key: " + str(self.target_key) + ", type: merge")
        
    def get_translator_type(self):    
        return self.translator_type
        
    def get_source_key(self):
        return self.source_keys
    
    def get_target_key(self):
        return self.target_key
    
    def get_value(self, source_key_values):
        list_of_values = []
        for i in range(len(self.source_keys)):
            v = source_key_values.get(self.source_keys[i])
            if len(v) > 0:
                list_of_values.append(v)
        if any(isinstance(i, list) for i in list_of_values):
            if len(list_of_values) == 2:        # case: multiple values with 2 merge items
                list1 = list_of_values[0]
                list2 = list_of_values[1]
                v_merged = [m + self.merge_symbol + n for m,n in zip(list1,list2) if m and n != "none"]
            if len(list_of_values) == 3:        # case: multiple values with 3 merge items
                list1 = list_of_values[0]
                list2 = list_of_values[1]
                list3 = list_of_values[2]
                v_merged = [m + self.merge_symbol + n + self.merge_symbol + p for m,n,p in zip(list1,list2,list3) if m and n and p != "none"]
        else:
            v_merged = self.merge_symbol.join(list_of_values)       
                                   
        return v_merged
    
    def get_priority(self):
        return self.priority
        