import unittest
import json
import sys
import os
sys.path.append('..')
from models.ReaderFactory import ReaderFactory
from api.globals import MAPPINGS
from api.resources import read_all_config_files, read_config

class TestReader(unittest.TestCase):
    def setUp(self):
        read_all_config_files()
        self.reader = ReaderFactory.create_reader('plain/txt') 
    
    def test_TextReader(self):        
        for subdir, dirs, files in os.walk('./input'):
            for file in files:
                path = os.path.join(subdir, file)
                test_input = open(path)    
                source_key_value = self.reader.read(test_input.readline().encode(), 'harvester')
                
        self.assertEqual("2019-04-04", source_key_value.get("dates.date"))
        self.assertEqual(["Selent","Schembera"], source_key_value.get("contact.familyName"))
        self.assertEqual("Data Manager", source_key_value.get("contributor.role"))
        self.assertEqual(["German", "English"], source_key_value.get("subjects.subject.lang"))
        