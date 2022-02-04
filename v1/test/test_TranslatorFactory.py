import unittest
import json
import sys
import os
sys.path.append('..')
from models.TranslatorFactory import TranslatorFactory
from models.Translator import BaseTranslator, MergeTranslator, AdditionTranslator

class TestTranslatorFactory(unittest.TestCase):
    def setUp(self):
        self.f = TranslatorFactory()
        pass 
    
    def test_create_translator(self):      
        #test engMeta yaml with merge  
        t = self.f.create_translator({"source_key": ["/dataset/creator/givenName", "/dataset/creator/familyName"], "target_key": "authorName", "type": "merge", "join_symbol": " ", "priority": 2})
        self.assertEqual(t.source_keys, ["/dataset/creator/givenName", "/dataset/creator/familyName"])
        self.assertEqual(t.target_key, "authorName")
        self.assertEqual(t.translator_type, "merge")
        self.assertEqual(t.merge_symbol, " ")
        self.assertEqual(t.priority, 2)
        # test copy translator
        tc = self.f.create_translator({'target_key': 'dates.date'})
        self.assertEqual(tc.source_key, "dates.date")
        self.assertEqual(tc.target_key, "dates.date")
        self.assertEqual(tc.priority, 1)
        # test normal translator with priority
        t2 = self.f.create_translator({"priority": 2, "source_key": "creator.name", "target_key": "authorName"})
        self.assertEqual(t2.source_key, "creator.name")
        self.assertEqual(t2.target_key, "authorName")
        self.assertEqual(t2.priority, 2)
        # test merge translator
        t3 = self.f.create_translator({"source_key": ["creator.givenName", "creator.familyName"],"target_key": "authorName", "type": "merge", "join_symbol": " "})
        self.assertEqual(t3.source_keys, ["creator.givenName", "creator.familyName"])
        self.assertEqual(t3.target_key, "authorName")
        self.assertEqual(t3.priority, 1)
        self.assertEqual(t3.translator_type, "merge")
        # test addition translator
        t4 = self.f.create_translator({"source_key": "title", "target_key": "dateOfDeposit", "type": "addition", "class": "DateAdder"})
        self.assertEqual(t4.source_key, "title")
        self.assertEqual(t4.target_key, "dateOfDeposit")
        self.assertEqual(t4.priority, 1)
        self.assertEqual(t4.class_name, "DateAdder")
        self.assertEqual(t4.translator_type, "addition")