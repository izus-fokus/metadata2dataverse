import unittest
import json
import sys
sys.path.append('..')
from models.Config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config('Harvester', 'menschenlesbare Beschreibung der Konfiguration/des Mappings (welches Metadatenformat wird in welcher Version unterstützt)', 'text/plain') 
    
    def test_add_and_get_translator(self):        
        # test copy translator
        self.config.add_translator({'target_key': 'dates.date'})
        self.assertIn("dates.date", self.config.translators_dict)
        t = self.config.get_translator("dates.date")
        self.assertEqual(t.source_key, "dates.date")
        self.assertEqual(t.target_key, "dates.date")
        self.assertEqual(t.priority, 1)
        # test normal translator with priority
        self.config.add_translator({"source_key": "creator.name", "target_key": "authorName", "priority": 2})
        self.assertIn("creator.name", self.config.translators_dict)
        t2 = self.config.get_translator("creator.name")
        self.assertEqual(t2.source_key, "creator.name")
        self.assertEqual(t2.target_key, "authorName")
        self.assertEqual(t2.priority, 2)
        # test merge translator
        self.config.add_translator({"source_key": ["creator.givenName", "creator.familyName"],"target_key": "authorName", "type": "merge", "join_symbol": " "})
        self.assertIn("creator.givenName", self.config.translators_dict)
        t3 = self.config.get_translator("creator.givenName")
        self.assertEqual(t3.source_key, ["creator.givenName", "creator.familyName"])
        self.assertEqual(t3.target_key, "authorName")
        self.assertEqual(t3.priority, 1)
        self.assertEqual(t3.translator_type, "merge")
        # test addition translator
        self.config.add_translator({"source_key": "title", "target_key": "dateOfDeposit", "type": "addition", "class": "DateAdder"})
        self.assertIn("title", self.config.translators_dict)
        t4 = self.config.get_translator("title")
        self.assertEqual(t4.source_key, "title")
        self.assertEqual(t4.target_key, "dateOfDeposit")
        self.assertEqual(t4.priority, 1)
        self.assertEqual(t4.class_name, "DateAdder")
        self.assertEqual(t4.translator_type, "addition")
        
    def test_add_rule(self):
        self.config.add_rules({"trigger": "contact.role","type": "rule","priority": 1,"trigger_values": ["Producer", "Distributor"], "Producer": [{"source_key": "contact.name", "target_key": "producerName"}, {"source_key": "contact.affiliation.name", "target_key": "producerAffiliation"}, {"source_key": "contact.affiliation.id", "target_key": "producerAbbreviation"}], "Distributor": [{"source_key": "contact.name", "target_key": "distributorName"}, {"source_key": "contact.affiliation.name", "target_key": "distributorAffiliation"}, {"source_key": "contact.affiliation.id", "target_key": "distributorAbbreviation"}]})
        self.assertIn("contact.role", self.config.rules_dict)
        inner_dict = self.config.rules_dict.get("contact.role")
        self.assertIn("Producer", inner_dict)
        t_list = inner_dict.get("Producer")
        self.assertEqual(t_list[0].source_key, "contact.name")
        self.assertEqual(t_list[0].target_key, "producerName")
    
        
           