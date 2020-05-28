import unittest
import json
import sys
sys.path.append('..')

from api.resources import read_config

class TestResources(unittest.TestCase):
    def setUp(self):
        pass

    def test_read_config(self):
        test_yaml = """description: menschenlesbare Beschreibung der Konfiguration/des Mappings (welches Metadatenformat wird in welcher Version unterstützt)

format: text/plain
scheme: Harvester

mapping:
- target_key: title
- source_key: [creator.givenName, creator.familyName]
  target_key: authorName
  type: merge
  join_symbol: " "
  priority: 1

rules:
- trigger: contact.role
  type: rule
  priority: 1
  trigger_values: [Producer, Distributor]
  Producer: [{source_key: contact.name, target_key: producerName}, {source_key: contact.affiliation.name, target_key: producerAffiliation}, {source_key: contact.affiliation.id, target_key: producerAbbreviation}]
  Distributor: [{source_key: contact.name, target_key: distributorName}, {source_key: contact.affiliation.name, target_key: distributorAffiliation}, {source_key: contact.affiliation.id, target_key: distributorAbbreviation}]

"""
        test_config = read_config(test_yaml)        
        self.assertEqual(test_config.description, "menschenlesbare Beschreibung der Konfiguration/des Mappings (welches Metadatenformat wird in welcher Version unterstützt)")
        self.assertEqual(test_config.format, "text/plain")
        self.assertEqual(test_config.scheme, "Harvester")