from abc import abstractstaticmethod, ABCMeta
from flask import g
from api.globals import MAPPINGS     # global variables
from lxml import etree as ET
from jsonpath import JSONPath
import json
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
    """ Reads *.txt file, extracts source keys and values, and returns source_key_value dictionary. """
    def __init__(self):        
        pass


    def __repr__(self):
        pass

    
    def read(text_data, mapping):
        """ Reads input line by line and checks if source_key is in translators_dict of scheme.  
        
        Returns source_key_value dictionary with source_key as key and values as value.  
        
        Parameters
        ---------
        text_data : opened txt-file
        mapping : Config obj
        
        Returns
        ---------
        source_key_values : dict 
        """
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
    """ Reads *.xml file, extracts source keys and values, and returns source_key_value dictionary. """
    def __init__(self):
        pass


    def __repr__(self):
        pass


    def read(xml_data, mapping):
        """ Goes through source keys of mapping, and extracts values from xml file.  
        
        Returns source_key_value dictionary with source_key as key and values as value.  
        
        Parameters
        ---------
        text_data : opened xml-file
        mapping : Config obj
        
        Returns
        ---------
        source_key_values : dict 
        """
        # get all source keys of scheme
        list_of_source_keys = mapping.get_source_keys()
        list_of_source_keys = list(dict.fromkeys(list_of_source_keys))  #remove duplicates
        # get namespaces
        namespaces = mapping.namespaces        
        root = ET.fromstring(xml_data)
        source_key_value = {}        
        for source_key in list_of_source_keys:
            print(source_key)
            if source_key.count("/") > 2 and source_key.count("@") == 0:        # case nested source_key
                main_key = source_key.rsplit("/", 1)[0]
            else:
                main_key = source_key
            try:
                elements = root.xpath("." + main_key, namespaces=namespaces)   
                print("elements: ",elements)
            except:
                g.warnings.append(source_key + " not a valid X-Path. Please check your YAML File.")
                continue            
            if len(elements) > 0:
                if isinstance(elements[0], str):
                    for i in range(len(elements)):
                        values.append(elements[i])
                    source_key_value[source_key] = values
                    continue
                elif len(elements[0].text.rstrip().lstrip()) > 0:   # single (compound) source_key
                    values = []
                    for i in range(len(elements)):
                        values.append(elements[i].text)
                    source_key_value[source_key] = values
                else:                                   # multiple compound source_key 
                    number_of_childs = len(elements)  
                    parent = main_key
                    child = source_key.rsplit("/",1)[1]     
                    values = []     # values of source_key      
                    if number_of_childs == 1:
                        value = root.xpath("." + parent  + "/" + child, namespaces=namespaces)  
                        if len(value) > 0:
                            for i in range(len(value)):
                                values.append(value[i].text)
                        else:
                            values.append('none')
                        source_key_value[source_key] = values
                        print(values)
                    else:
                        for i in range(number_of_childs):
                            i += 1
                            value = root.xpath("." + parent + "[" + str(i) + "]" + "/" + child, namespaces=namespaces) 
                            print("." + parent + "[" + str(i) + "]" + "/" + child)
                            
                            if len(value) > 0:
                                values.append(value[0].text)
                            else:
                                values.append('none')
                            source_key_value[source_key] = values
                            print(values)
        return source_key_value


class JSONReader(Reader):    
    """ Reads *.json file, extracts source keys and values, and returns source_key_value dictionary. """
    def __init__(self):
        pass


    def __repr__(self):
        pass
    

    def read(json_data, mapping):
        """ Goes through source keys of mapping, and extracts values from json file.  
        
        Returns source_key_value dictionary with source_key as key and values as value.  
        
        Parameters
        ---------
        text_data : opened xml-file
        mapping : Config obj
        
        Returns
        ---------
        source_key_values : dict 
        """
        json_input = json.loads(json_data)
        list_of_source_keys = mapping.get_source_keys()
        list_of_source_keys = list(dict.fromkeys(list_of_source_keys))  #remove duplicates
        source_key_value = {}
        for source_key in list_of_source_keys:            
            if "[*]" in source_key:                     # multiple compound source_key 
                main_key = source_key.split(".",1)[0]   
                try:
                    elements = JSONPath("$.{}".format(main_key)).parse(json_input)
                except:
                    g.warnings.append(source_key + " not a valid JSON-Path. Please check your YAML File.")
                    continue
            else:                                       # single (compound) source_key
                try:
                    elements = JSONPath("$.{}".format(source_key)).parse(json_input)
                except:
                    g.warnings.append(source_key + " not a valid JSON-Path. Please check your YAML File.")
                    continue
            if len(elements) > 0:
                if isinstance(elements[0], str):   # single (compound) source_key
                    values = elements
                elif isinstance(elements[0], list):  # single (compound) source_key
                    values = elements[0]
                else:                               # multiple compound source_key 
                    number_of_childs = len(elements)  
                    parent = source_key.split("[*]",1)[0]
                    child = source_key.split(".",1)[1]     
                    values = []     # values of source_key      
                    for i in range(number_of_childs):
                        value = JSONPath("$.{}[{}].{}".format(parent,i,child)).parse(json_input)  
                        if len(value) > 0:
                            values.append(value[0])
                        else:
                            values.append('none')
                source_key_value[source_key] = values
        return source_key_value
