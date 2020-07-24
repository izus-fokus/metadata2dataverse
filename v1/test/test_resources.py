import unittest
import json
import sys
import os
sys.path.append('..')

from api.resources import read_config, read_all_config_files, read_tsv
from api.globals import DV_FIELD, DV_MB, DV_CHILDREN

class TestResources(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_read_config(self):
        for subdir, dirs, files in os.walk('./config'):
            for file in files:
                path = os.path.join(subdir, file)
                test_yaml = open(path)            
                test_config = read_config(test_yaml)        
                self.assertEqual(test_config.description, "menschenlesbare Beschreibung der Konfiguration/des Mappings (welches Metadatenformat wird in welcher Version unterstützt)")
                self.assertEqual(test_config.format, "text/plain")
                self.assertEqual(test_config.scheme, "Harvester")        
    
    def test_read_tsv(self):
        for subdir, dirs, files in os.walk('./tsv'):
            for file in files:
                path = os.path.join(subdir, file)
                test_tsv = open(path)            
                read_tsv(test_tsv)
        print(DV_FIELD, DV_MB, DV_CHILDREN)
           