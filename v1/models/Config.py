class Config(object):
    ''' object after parsing a mapping file '''

    def __init__(self, scheme, description, format, translators, rules_dict):
        ''' Constructor '''
        self.scheme = scheme
        self.description = description
        self.format = format
        self.translators = translators
        self.rules_dict = rules_dict
                   
    