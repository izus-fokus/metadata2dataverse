from abc import ABCMeta
from flask import g
from lxml import etree as ET
from jsonpath import JSONPath
import json
from builtins import isinstance
from rdflib import Graph

class ReaderFactory(object):
    def __init__(self):
        pass

    @staticmethod
    def create_reader(content_type):
        if content_type == 'plain/txt':
            return TextReader
        if content_type == 'text/xml':
            return XMLReader
        if content_type == 'application/json':
            return JSONReader
        if content_type == 'application/jsonld':
            return JSONLDReader
        return None


class Reader(metaclass=ABCMeta):
    """ Factory-Class """

    def read(self, text_data, mapping):
        """ Translator Interface """


class TextReader(Reader):
    """ Reads *.txt file, extracts source keys and values, and returns source_key_value dictionary. """
    def __init__(self):
        pass


    def __repr__(self):
        pass


    def read(self, text_data, mapping):
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
        if isinstance(text_data, bytes):
            text_data = text_data.decode()
        # get all source keys of scheme
        list_of_source_keys = mapping.get_source_keys()
        source_key_value = {}
        for line in text_data.splitlines():
            if len(line) > 1:   # ignore empty lines
                splitted_line = line.split(":")
                source_key = splitted_line[0]
                if source_key not in list_of_source_keys:
                    g.warnings.append(source_key + " not found in scheme mapping - Check your Yaml Mapping File")
                    continue
                values = splitted_line[1]
                splitted_values = values.split(',')
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


    def read(self, xml_data, mapping):
        """ Goes through source keys of mapping, and extracts values from xml file.

        Returns source_key_value dictionary with source_key as key and values as value.

        Parameters
        ---------
        xml_data : opened xml-file
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
        values = []
        for source_key in list_of_source_keys:

            if source_key.count("/") > 2 and source_key.count("@") == 0:        # case nested source_key
                main_key = source_key.rsplit("/", 1)[0]
            else:
                main_key = source_key
            try:
                elements = root.xpath("." + main_key, namespaces=namespaces)

            except IndexError as e:
                g.warnings.append(source_key + " not a valid X-Path. Please check your YAML File. Error: " + str(e))
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
                        #print(values)
                    else:
                        for i in range(number_of_childs):
                            i += 1
                            value = root.xpath("." + parent + "[" + str(i) + "]" + "/" + child, namespaces=namespaces)
                            #print("." + parent + "[" + str(i) + "]" + "/" + child)

                            if len(value) > 0:
                                values.append(value[0].text)
                            else:
                                values.append('none')
                            source_key_value[source_key] = values
        return source_key_value


class JSONReader(Reader):
    """ Reads *.json file, extracts source keys and values, and returns source_key_value dictionary. """
    def __init__(self):
        pass


    def __repr__(self):
        pass


    def read(self, json_data, mapping):
        """ Goes through source keys of mapping, and extracts values from json file.

        Returns source_key_value dictionary with source_key as key and values as value.

        Parameters
        ---------
        json_data : opened xml-file
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
            d_key, main_key = None, None
            if "#" in source_key:
                d_key, source_key = source_key.split("#")
            # field selectors already have correct num of elements so we skip the logic below
            if source_key.endswith(")") or "[*]" not in source_key:
                try:
                    elements = JSONPath("$.{}".format(source_key)).parse(json_input)
                except IndexError as e:
                    g.warnings.append(
                        source_key + " not a valid JSON-Path. Please check your mapping config file. Error: " + str(e))
                    continue
            #TODO: should also work with ".*" (not only [*])
            else:                     # multiple compound source_key
                main_key = source_key.split(".",1)[0]
                try:
                    elements = JSONPath("$.{}".format(main_key)).parse(json_input)
                except IndexError as e: #TODO: forward concrete jsonpath exeption to the user
                    g.warnings.append(source_key + " not a valid JSON-Path. Please check your YAML File. Error: " + str(e))
                    continue
            if len(elements) > 0: # if we found something
                # single (compound) source_key or
                # field selectors that has already correct num of elements
                if main_key is None and (isinstance(elements[0], str) or source_key.endswith(")")):
                    values = elements
                elif main_key is None and isinstance(elements, list):  # single (compound) source_key
                    values = elements[0]
                elif type(elements[0]) is dict:  # multiple compound source_key
                    number_of_childs = len(elements)
                    parent = source_key.split("[*]", 1)[0]
                    child = source_key.split(".", 1)[1]
                    values = []  # values of source_key
                    for i in range(number_of_childs):
                        value = JSONPath("$.{}[{}].{}".format(parent, i, child)).parse(json_input)
                        if len(value) > 0:
                            values.append(value[0])
                        else:
                            values.append('none')
                    if all(['none' == elem for elem in values]):
                        continue
                else:
                    number_of_childs = len(elements)
                    values = []  # values of source_key
                    for i in range(number_of_childs):
                        value = elements[i]
                        if len(value) > 0:
                            values.append(value)
                        else:
                            values.append('none')
                    if all(['none' == elem for elem in values]):
                        continue
                if d_key:
                    source_key_value["{}#{}".format(d_key, source_key)] = {d_key: values}
                else:
                    source_key_value[source_key] = values
        return source_key_value
class JSONLDReader(Reader):
    """ Reads *.jsonld file, extracts source keys and values, and returns source_key_value dictionary. """

    def __init__(self):
        pass

    def __repr__(self):
        pass

    def read(self, jsonld_data, mapping):
        """ Goes through source keys of mapping, and extracts values from jsonld file.

        Returns source_key_value dictionary with source_key as key and values as value.

        Parameters
        ---------
        jsonld_data : opened jsonld-file
        mapping : Config obj

        Returns
        ---------
        source_key_values : dict
        """

        graphElement = Graph()
        graphElement.parse(jsonld_data, format="json-ld")
        # v = graphElement.serialize(format="json-ld")
        key_values = {}
        list_of_source_keys = mapping.get_source_keys()
        list_of_source_keys = list(dict.fromkeys(list_of_source_keys))
        for source_key in list_of_source_keys:
            #print("source_key: ", source_key)
            elements = []
            main_key = ""
            main_keys=[]

            # Check if the source key contains "#" for nested source keys
            if "#" in source_key:
                elements = source_key.split("#")
                #print("elements:",elements)

            # Check if the source key contains "*" for a main key
            elif "*" in source_key:
                main_key = source_key.replace("[*]", "")

            else:
                main_key = source_key

            if main_keys:
                for m in main_keys:
                    main_key=m

            # If a main key is present, query the data and store the results
            if main_key != "":
                #print("main_key: ",main_key, "\n")
                if main_key not in key_values:
                    key_values[main_key] = []
                    main_query = (
                        """SELECT ?subj ?prop ?obj
                              WHERE {
                                 ?subj ?prop ?obj .
                                 ?subj ?prop """
                        + main_key
                        + """
                              }"""
                    )
                    for row in graphElement.query(main_query):
                        s = row.subj.toPython()
                        # o = row.obj.toPython()
                        # print(row)
                        key_values[main_key].append(s)
                    #print("key_values:",key_values)

            # If there are nested elements, query and store data for each level
            if len(elements) > 1:
                # parent_temp = {}
                # parent_key_order = []

                # Iterate through each level in the elements
                for i in range(0, len(elements)-1):
                    parent = elements[i]
                    child = elements[i+1]
                    parent_query = (
                        """SELECT ?subj ?prop ?obj
                        WHERE {
                           ?subj ?prop ?obj .
                           ?subj ?prop """
                        + parent
                        + """
                        }"""
                    )
                    child_query = (
                        """SELECT ?subj ?prop ?obj
                        WHERE {
                           ?subj ?prop ?obj .
                           ?subj """
                        + child
                        + """ ?obj
                        }"""
                    )
                    # objects = {}
                    temp = {}
                    key_order = []

                    # Query and store data for the parent element
                    for row in graphElement.query(parent_query):
                        # print("row: ",row)
                        s = row.subj.toPython()
                        temp[s] = None
                        key_order.append(s)

                    # Query and store data for the child element
                    for row in graphElement.query(child_query):
                        o = row.obj.toPython()
                        s = row.subj.toPython()
                        # p = row.subj.toPython()
                        #print(child_query)
                        if s in temp:
                            #print("DEBUG: o: ",s, " temp: ", temp,"\n")
                            if temp[s] is None:
                                temp[s] = str(o)
                            else:
                                temp[s]=temp[s]+" , "+str(o)
                    key_values[source_key] = []

                    # Populate key values based on the order of keys
                    for key in key_order:

                        if temp[key] is None:
                            key_values[source_key].append('None')
                        else:
                            key_values[source_key].append(temp[key])
                    # parent_temp = temp
                    # parent_key_order = key_order

        # Remove keys with empty values (None, empty strings, empty lists, empty dictionaries)
        key_values = {key: value for key, value in key_values.items() if value}
        return key_values