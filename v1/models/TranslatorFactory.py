from models.Translator import BaseTranslator, MergeTranslator, AdditionTranslator, DateTranslator

class TranslatorFactory(object):
    ''' Gets a config file and creates translators. '''

    def __init__(self):
        ''' Constructor '''
        pass

    @staticmethod
    def create_translator(translator_yaml):
        """ Generates a translator object out of yaml translators.

        Parameters
        ---------
        translator_yaml : yaml dict

        Returns
        ---------
        BaseTranslator obj or AdditionTranslator obj or MergeTranslator obj
        """
        source_key = translator_yaml.get('source_key', None)
        target_key = translator_yaml.get('target_key', None)
        priority = translator_yaml.get('priority', 1)
        translator_type = translator_yaml.get('type', None)
        join_symbol = translator_yaml.get('join_symbol', None)
        class_name = translator_yaml.get('class', None)
        if(len(translator_yaml) == 1):                 # case 1: copy translator
            source_key = target_key
            translator = BaseTranslator(source_key, target_key, priority)
            return translator
        if("type" in translator_yaml):
            if(translator_yaml["type"] == "addition"):  # case 3: addition translator
                translator = AdditionTranslator(source_key, target_key, class_name, translator_type, priority)
                return translator
            if(translator_yaml["type"] == "merge"):     # case 4: merge translator
                translator = MergeTranslator(source_key, target_key, priority, translator_type, join_symbol)
                return translator
            if(translator_yaml["type"] == "date"):     # case 5: date translator
                print("Date translator detected")
                translator = DateTranslator(source_key, target_key, priority, translator_type)
                return translator
        else:                                           # case 2: normal translator
            translator = BaseTranslator(source_key, target_key, priority)
            return translator