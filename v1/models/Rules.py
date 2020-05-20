"""
Created on 23.03.2020

@author: annekreuter
"""


class Rules(object):
    """
    classdocs
    """


    def __init__(self, trigger, dict_for_rules, priority = 1):
        """
        Constructor
        param rule_translators: dictionary with trigger_value (key) and list of translators (value)
        """
        self.trigger = trigger
        self.dict_for_rules = dict_for_rules
        self.priority = priority
        
        for trigger_value in dict_for_rules:
            t = Translate(dict_for_rules[trigger_value])
            
        