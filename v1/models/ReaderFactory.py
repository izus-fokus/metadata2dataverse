from abc import abstractstaticmethod, ABCMeta
from api.globals import SOURCE_KEYS     # global variables

class ReaderFactory(object):
    def __init__(self):
        pass
       
    def create_reader(content_type): 
        if (content_type == 'plain/txt'):
            return TextReader
        if (content_type == 'text/xml'):
            return XMLReader
        if (content_type == 'application/json'):
            return JSONReader          
     

class Reader(metaclass=ABCMeta):
    """ Factory-Class """

    def read():
        """ Translator Interface """ 
        
        
class TextReader(Reader):    

    def __init__(self):        
        pass
    
    def __repr__(self):
        pass
        
    def read(text_data):
        translators = []
        print(SOURCE_KEYS)
        for line in text_data.splitlines():
            line = line.decode("utf-8")
            splitted_line = line.split(":")
            source_key = splitted_line[0]
            print(source_key)
            values = splitted_line[1]
            translator = SOURCE_KEYS.get(source_key)
            print(translator)
            translator.set_value(values)
            translators.append(translator)
        return translators
    
    
        
class XMLReader(Reader):    
    def __init__(self):
        pass
    
    def __repr__(self):
        pass
    
    def read(self, xml_data):
        return self.source_key
    
class JSONReader(Reader):    
    def __init__(self):
        pass
    
    def __repr__(self):
        pass
    
    def read(self, json_data):
        return self.source_key
        
        
