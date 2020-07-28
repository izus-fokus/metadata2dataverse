from abc import abstractstaticmethod, ABCMeta
from api.globals import MAPPINGS     # global variables

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
        
    # gets input and scheme. 
    # reads input line by line and checks if source_key is in translators_dict of scheme.     
    def read(text_data, list_of_source_keys):
        source_key_value = {}
        for line in text_data.splitlines():            
            line = line.decode("utf-8")
            if len(line) > 1:   # ignore empty lines
                splitted_line = line.split(":")
                source_key = splitted_line[0]
                if source_key not in list_of_source_keys:
                    print(source_key, " not found in scheme mapping - Check your Yaml Mapping File")
                    continue        
                values = splitted_line[1]
                splitted_values = values.split(",")
                source_key_value[source_key] = []
                for value in splitted_values:
                    if len(value) > 1:
                        source_key_value[source_key].append(value.strip())
        return source_key_value
    
    
        
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
        
        
