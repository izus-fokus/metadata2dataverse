class Field(object):
    ''' object after parsing a tsv file '''

    controlled_vocabulary = []
    def __init__(self, multiple, type_class, parent, metadata_block):
        ''' Constructor '''
        self.multiple = multiple
        self.type_class = type_class
        self.parent = parent
        self.metadata_block = metadata_block
        
    def set_controlled_vocabulary(self, controlled_vocabulary):
        self.controlled_vocabulary.append(controlled_vocabulary)
                   
    