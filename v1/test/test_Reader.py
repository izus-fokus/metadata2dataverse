import unittest
import sys
import os
sys.path.append('..')
from models.ReaderFactory import ReaderFactory
from api.globals import MAPPINGS


class TestReader(unittest.TestCase):
    def setUp(self):
        self.reader = ReaderFactory.create_reader('plain/txt')

    def test_TextReader(self):        
        for subdir, dirs, files in os.walk('./input'):
            for file in files:
                path = os.path.join(subdir, file)
                test_input = open(path)    
                source_key_value = self.reader.read(
                    test_input.read().encode(),
                    ['dates.date', 'creator.name', 'creator.affiliation', 'contributor.role'])
                test_input.close()

        self.assertEqual(["2019-04-04","",""], source_key_value.get("dates.date"))
        self.assertEqual(["Selent", "", "Schembera"], source_key_value.get("creator.name"))
        self.assertEqual(["IMS","",""], source_key_value.get("creator.affiliation"))
        self.assertNotEqual(
            ["German", "English"],
            source_key_value.get("subjects.subject.lang"))
