class Field(object):
    ''' object after parsing a tsv file '''

    
    def __init__(self, multiple, type_class, parent, metadata_block):
        ''' Constructor '''
        self.controlled_vocabulary = []
        self.multiple = (multiple == 'TRUE')
        self.type_class = type_class
        self.parent = parent
        self.metadata_block = metadata_block
        
    def __repr__(self):
        return "{multiple: " + str(self.multiple) + ", type class: " + self.type_class + ", parent: " + str(self.parent) + ", metadata block: " + self.metadata_block + ", controlled Vocabulary: " + str(self.controlled_vocabulary) +"}"
        
    def set_controlled_vocabulary(self, controlled_vocabulary):
        self.controlled_vocabulary.append(controlled_vocabulary)
        
        
                   
    