import unittest
import json
import sys
sys.path.append('..')
from models.Config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config('Harvester', 'menschenlesbare Beschreibung der Konfiguration/des Mappings (welches Metadatenformat wird in welcher Version unterstützt)', 'text/plain')
    
    def test_repr_(self):        
        print(self.config)       
    
    def test_add_translator(self):        
        self.config.add_translator({'target_key': 'dates.date'})
        self.assertEqual(self.config.translators_dict, {'dates.date': 'source key\\: dates.date\\, target key\\: dates.date'})
        print("get translator: ", self.config.get_translator("dates.date"))
    
        
           