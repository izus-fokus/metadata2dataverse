from flask import g
class Field(object):
    ''' object after parsing a tsv file '''

    
    def __init__(self, target_key, multiple, type_class, parent, metadata_block):
        ''' Constructor '''
        self.target_key = target_key
        self.controlled_vocabulary = []
        self.multiple = (multiple == 'TRUE')
        self.type_class = type_class
        self.parent = parent
        self.metadata_block = metadata_block
        
    def __repr__(self):
        return "{multiple: " + str(self.multiple) + ", type class: " + self.type_class + ", parent: " + str(self.parent) + ", metadata block: " + self.metadata_block + ", controlled Vocabulary: " + str(self.controlled_vocabulary) +"}"
        
    def set_controlled_vocabulary(self, controlled_vocabulary):
        self.controlled_vocabulary.append(controlled_vocabulary)
        
    def check_controlled_vocabulary(self, v):  
        if isinstance(v, list):
            v_new = []
            for value_ in v:
                if value_ in self.controlled_vocabulary:
                    v_new.append(value_)
                else:
                    g.warnings.append(self.target_key + " has a controlled vocabulary. " + value_ + " is not part of it. It has been removed. Allowed values are: " + str(self.controlled_vocabulary))
                    continue
        else:
            if v in self.controlled_vocabulary:      
                return v
            else: 
                g.warnings.append(self.target_key + " has a controlled vocabulary. " + v +" is not part of it. It has been removed. Allowed values are: " + str(self.controlled_vocabulary))
                v_new = []
        return v_new
    