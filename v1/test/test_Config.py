import unittest
import json
import sys
sys.path.append('..')
from models.Config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config('Harvester', 'menschenlesbare Beschreibung der Konfiguration/des Mappings (welches Metadatenformat wird in welcher Version unterstützt)', 'text/plain') 
    
    def test_add_translator(self):        
        # test copy translator
        self.config.add_translator({'target_key': 'dates.date'})
        self.assertIn('dates.date', self.config.translators_dict)
        self.config.add_translator({"source_key": ["creator.givenName", "creator.familyName"],"target_key": "authorName", "type": "merge", "join_symbol": " "})
        self.assertIn('creator.givenName', self.config.translators_dict)
        self.assertIn('creator.familyName', self.config.translators_dict)
        
    def test_add_rule(self):
        self.config.add_rules({"trigger": "contact.role","type": "rule","priority": 1,"trigger_values": ["Producer", "Distributor"], "Producer": [{"source_key": "contact.name", "target_key": "producerName"}, {"source_key": "contact.affiliation.name", "target_key": "producerAffiliation"}, {"source_key": "contact.affiliation.id", "target_key": "producerAbbreviation"}], "Distributor": [{"source_key": "contact.name", "target_key": "distributorName"}, {"source_key": "contact.affiliation.name", "target_key": "distributorAffiliation"}, {"source_key": "contact.affiliation.id", "target_key": "distributorAbbreviation"}]})
        self.assertIn("contact.role", self.config.rules_dict)
        inner_dict = self.config.rules_dict.get("contact.role")
        self.assertIn("Producer", inner_dict)
        t_list = inner_dict.get("Producer")
        self.assertEqual(t_list[0].source_key, "contact.name")
        self.assertEqual(t_list[0].target_key, "producerName")