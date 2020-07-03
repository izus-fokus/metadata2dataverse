from abc import abstractstaticmethod, ABCMeta

class Reader(metaclass=ABCMeta):
    """ Factory-Class """

    def set_value():
        """ Translator Interface """ 
        
        
class TextReader(Reader):    

    def __init__(self, source_key, value):        
        self.source_key = source_key
        self.value = value 
        self.priority = priority 
    
    def __repr__(self):
        return ("source key: " + str(self.source_key) + ", value: " + str(self.value))
        
    def get_value(self):
        return self.value
    
    
        
class XmlReader(Reader):    
    def __init__(self, class_name, translator_type="addition",  *args, **kwargs):
        super(AdditionTranslator, self).__init__(*args, **kwargs)
        self.class_name = class_name
        self.translator_type = translator_type
    
    def __repr__(self):
        return ("source key: " + self.source_key + ", target key: " + self.target_key)
    
    def get_value(self):
        return self.source_key
        
        
