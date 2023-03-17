import unittest
import sys
import os
import yaml
sys.path.append('..')
from models.ReaderFactory import ReaderFactory
from api.resources import read_config, read_all_scheme_files
from api.globals import MAPPINGS,DV_FIELD, DV_CHILDREN, DV_MB 
from api.app import create_app


class TestReader(unittest.TestCase):
    def setUp(self):
        self.reader = ReaderFactory.create_reader('plain/txt')
        self.app = create_app()
        self.app.testing = True
        self.context = self.app.app_context()
        with self.context:
            read_all_scheme_files()
            mapping_file = open('./resources/config/harvester.yml')
            
            self.mapping = read_config(mapping_file)
            mapping_file.close()

    def test_TextReader(self):        
        for subdir, dirs, files in os.walk('./input'):
            for file in files:
                path = os.path.join(subdir, file)
                test_input = open(path)
                with self.context:
                    source_key_value = self.reader.read(
                        test_input.read().encode(),
                        self.mapping)
                test_input.close()

        self.assertEqual(["2019-04-04","",""], source_key_value.get("dates.date"))
        self.assertEqual(["Selent", "", "Schembera"], source_key_value.get("creator.name"))
        self.assertEqual(["IMS","",""], source_key_value.get("creator.affiliation"))
        self.assertNotEqual(
            ["German", "English"],
            source_key_value.get("subjects.subject.lang"))
