from abc import ABCMeta

from dateutil import parser

from models.AdditionTranslators import main


class Translator(metaclass=ABCMeta):
    """ Factory-Class """

    def get_source_key():
        """ Translator Interface """
    def get_target_key():
        """ Translator Interface """
    def get_value():
        """ Translator Interface """
    def get_priority():
        """ Translator Interface """


class BaseTranslator(Translator):
    def __init__(self, source_key, target_key, priority = 1):
        self.source_key = source_key
        self.target_key = target_key
        self.priority = priority

    def __repr__(self):
        return ("source key: " + str(self.source_key) + ", target key: " + str(self.target_key))

    def get_source_key(self):
        return self.source_key

    def get_target_key(self):
        return self.target_key

    def get_value(self,source_key_values):
        v = source_key_values.get(self.source_key)
        return v

    def get_priority(self):
        return self.priority


class AdditionTranslator(Translator):
    def __init__(self, source_key, target_key, class_name, translator_type = "addition", priority = 1):
        self.source_key = source_key
        self.target_key = target_key
        self.priority = priority
        self.class_name = class_name
        self.translator_type = translator_type

    def __repr__(self):
        return ("source key: " + str(self.source_key) + ", target key: " + str(self.target_key))

    def get_translator_type(self):
        return self.translator_type

    def get_source_key(self):
        return self.source_key

    def get_target_key(self):
        return self.target_key

    def get_value(self, source_key_values, t_key=None):
        klass = globals()[self.class_name]
        value = main(self.source_key, self.target_key, source_key_values, t_key)
        return value

    def get_priority(self):
        return self.priority


class MergeTranslator(Translator):
    def __init__(self, source_keys, target_key, priority = 1, translator_type = "merge", merge_symbol = " "):
        self.source_keys = source_keys
        self.target_key = target_key
        self.priority = priority
        self.translator_type = translator_type
        self.merge_symbol = merge_symbol

    def __repr__(self):
        return ("source keys: " + str(self.source_keys) + ", target key: " + str(self.target_key) + ", type: merge")

    def get_translator_type(self):
        return self.translator_type

    def get_source_key(self):
        return self.source_keys

    def get_target_key(self):
        return self.target_key

    def get_value(self, source_key_values):
        list_of_values = []
        for i in range(len(self.source_keys)):
            try:
                v = source_key_values.get(self.source_keys[i])
                if len(v) > 0:
                    list_of_values.append(v)
            except:
                continue
        if any(isinstance(i, list) for i in list_of_values):
            #TODO: should be more generic: for all possible numbers of merge items, not just 1-3
            if len(list_of_values) == 1:        # case: multiple values with 1 merge items
                list1 = list_of_values[0]
                v_merged = list1
            if len(list_of_values) == 2:        # case: multiple values with 2 merge items
                list1 = list_of_values[0]
                list2 = list_of_values[1]
                #TODO: do not skip here values (if clause), other rules might apply for them;
                #      instead, skip if all target keys of an compound are 'none'
                v_merged = [m + self.merge_symbol + n for m,n in zip(list1,list2) if m and n != "none"]
            if len(list_of_values) == 3:        # case: multiple values with 3 merge items
                list1 = list_of_values[0]
                list2 = list_of_values[1]
                list3 = list_of_values[2]
                v_merged = [m + self.merge_symbol + n + self.merge_symbol + p for m,n,p in zip(list1,list2,list3) if m and n and p != "none"]
        else:
            v_merged = self.merge_symbol.join(list_of_values)

        return v_merged

    def get_priority(self):
        return self.priority

class DateTranslator(Translator):
    def __init__(self, source_key, target_key, priority = 1, translator_type = "date"):
        """
        Initialize a DateTranslator instance.

        Parameters
        ----------
        source_key : str
            The source key to extract date values from.
        target_key : str
            The target key to store the translated date values.
        priority : int, optional
            The priority of the translator (default is 1).
        translator_type : str, optional
            The type of translator, which is "date" by default.

        Returns
        -------
        None
        """
        self.source_key = source_key
        self.target_key = target_key
        self.priority = priority
        self.translator_type = translator_type

    def __repr__(self):
        """
        Return a string representation of the DateTranslator instance.

        Returns
        -------
        str
            A string containing source key, target key, and type information.
        """
        return ("source key: " + str(self.source_key) + ", target key: " + str(self.target_key) + ", type: date")

    def get_translator_type(self):
        """
        Get the type of the translator.

        Returns
        -------
        str
            The translator type, which is "date".
        """
        return self.translator_type

    def get_source_key(self):
        """
        Get the source key for date extraction.

        Returns
        -------
        str
            The source key.
        """
        return self.source_key

    def get_target_key(self):
        """
        Get the target key for storing translated date values.

        Returns
        -------
        str
            The target key.
        """
        return self.target_key



    def convert_to_desired_format(self,input_time):
        """
        Convert the input date/time to the desired format.

        Parameters
        ----------
        input_time : str
            The input date/time to be converted.

        Returns
        -------
        str
            The date in the format "yyyy-mm-dd", "yyyy-mm", or "yyyy" if successful.
            Returns "Invalid input time format" if parsing fails.
        """
        try:
            # Try parsing the input time using dateutil.parser
            parsed_time = parser.parse(input_time)
            #print(" \n Parsed time: ",parsed_time.hour)
            # Check if the time includes day, month, and year
            if parsed_time:
                if parsed_time.day:
                    # Format as yyyy-mm-dd
                    return parsed_time.strftime("%Y-%m-%d")
                elif parsed_time.month:
                    # Format as yyyy-mm
                    return parsed_time.strftime("%Y-%m")
                else:
                    # Format as yyyy
                    return parsed_time.strftime("%Y")
            else:
                return "Invalid input time format"

        except ValueError:
        # If parsing fails, return an error message
            return "None"


    def get_value(self, source_key_values):
        """
        Get the translated date values for the target key.

        Parameters
        ----------
        source_key_values : dict
            A dictionary containing source key-value pairs.

        Returns
        -------
        list
            A list of translated date values for the target key.
        """
        list_of_values = source_key_values.get(self.source_key)
        updated_list_of_values=[]
        if len(list_of_values) > 0:
                for v in list_of_values:
                    value=self.convert_to_desired_format(v)
                    updated_list_of_values.append(value)

        return updated_list_of_values

    def get_priority(self):
        """
        Get the priority of the translator.

        Returns
        -------
        int
            The priority value.
        """
        return self.priority
