class Config(object):
    ''' object after parsing a mapping file '''

    def __init__(self, scheme, description, format, translators_dict, rules_dict):
        ''' Constructor '''
        self.scheme = scheme
        self.description = description
        self.format = format
        self.translators_dict = translators_dict
        self.rules_dict = rules_dict

    def __repr__(self):
        return("scheme: " + self.scheme + ", description: " + self.description + ", format: " + self.format + ", translators: " + str(self.translators) + ", rules dict: " + str(self.rules_dict))
    
    def get_translator(self, source_key):
        return self.translators_dict.get(source_key)