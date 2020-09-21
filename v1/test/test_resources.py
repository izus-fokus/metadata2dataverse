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
                test_yaml.close()        
    
    def test_read_tsv(self):
        for subdir, dirs, files in os.walk('./tsv'):
            for file in files:
                path = os.path.join(subdir, file)
                test_tsv = open(path)            
                read_tsv(test_tsv)
                test_tsv.close()
        # test primitive without parent
        self.assertIn("title", DV_FIELD)
        field = DV_FIELD.get("title")
        self.assertEqual(field.multiple, False)
        self.assertEqual(field.type_class, "primitive")
        self.assertEqual(field.metadata_block, "citation")
        self.assertEqual(field.parent, None)
        # test primitive with parent
        self.assertIn("otherIdAgency", DV_FIELD)
        field2 = DV_FIELD.get("otherIdAgency")
        self.assertEqual(field2.multiple, False)
        self.assertEqual(field2.type_class, "primitive")
        self.assertEqual(field2.metadata_block, "citation")
        self.assertEqual(field2.parent, "otherId")
        # test compound
        self.assertIn("otherId", DV_FIELD)
        field3 = DV_FIELD.get("otherId")
        self.assertEqual(field3.multiple, True)
        self.assertEqual(field3.type_class, "compound")
        self.assertEqual(field3.metadata_block, "citation")
        self.assertEqual(field3.parent, None)
        # test controlled Vocabulary
        self.assertIn("subject", DV_FIELD)
        field4 = DV_FIELD.get("subject")
        self.assertEqual(field4.multiple, True)
        self.assertEqual(field4.type_class, "controlled_vocabulary")
        self.assertEqual(field4.metadata_block, "citation")
        self.assertEqual(field4.parent, None)
        self.assertEqual(field4.controlled_vocabulary, ["Agricultural Sciences","Arts and Humanities","Astronomy and Astrophysics","Business and Management","Chemistry","Computer and Information Science","Earth and Environmental Sciences","Engineering","Law","Mathematical Sciences","Medicine, Health and Life Sciences","Physics","Social Sciences","Other"])

        
           