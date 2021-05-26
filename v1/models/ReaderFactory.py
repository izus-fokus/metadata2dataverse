from abc import abstractstaticmethod, ABCMeta
from flask import g
from api.globals import MAPPINGS     # global variables
from lxml import etree as ET
from builtins import isinstance


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
    # returns source_key_value dictionary with source_key as key and values as value (can be a list or a single string)   
    def read(text_data, mapping):
        # get all source keys of scheme
        list_of_source_keys = mapping.get_source_keys()
        source_key_value = {}
        for line in text_data.splitlines():            
            line = line.decode("utf-8")
            if len(line) > 1:   # ignore empty lines
                splitted_line = line.split(":")
                source_key = splitted_line[0]
                if source_key not in list_of_source_keys:
                    g.warnings.append(source_key + " not found in scheme mapping - Check your Yaml Mapping File")
                    continue        
                values = splitted_line[1]
                splitted_values = values.split(",")
                if len(splitted_values) > 1:                            # multiple values
                    source_key_value[source_key] = []
                    for value in splitted_values:
                        if value.strip() == '':
                            source_key_value[source_key].append('none')
                        else:
                            source_key_value[source_key].append(value.strip())
                else:
                    source_key_value[source_key] = [splitted_values[0].strip()]   #single value
        return source_key_value


class XMLReader(Reader):    
    def __init__(self):
        pass

    def __repr__(self):
        pass

    def read(xml_data, mapping):
        # get all source keys of scheme
        list_of_source_keys = mapping.get_source_keys()
        # get namespaces
        namespaces = mapping.namespaces
        
        root = ET.fromstring(xml_data)
        
        source_key_value = {}
        for source_key in list_of_source_keys:
            try:
                elements = root.xpath("." + source_key, namespaces=namespaces)      
            except:
                g.warnings.append(source_key + " not a valid X-Path. Please check your YAML File.")
                continue
            if len(elements) > 1:               # multiple values
                source_key_value[source_key] = []
                for element in elements:
                    if element.text != None:
                        source_key_value[source_key].append(element.text)
            elif len(elements) == 1:            # single values or attribute value
                if isinstance(elements[0], str):    #attribute
                    source_key_value[source_key] = [elements[0]]
                else:
                    if elements[0].text != None:
                        source_key_value[source_key] = [elements[0].text]
        return source_key_value


class JSONReader(Reader):    
    def __init__(self):
        pass

    def __repr__(self):
        pass

    def read(self, json_data):
        return self.source_key
