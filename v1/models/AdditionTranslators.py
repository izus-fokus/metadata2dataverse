from datetime import date
import chevron

from api.globals import DV_FIELD


def main():
    today = date.today()
    date_formatted = today.strftime("%Y-%m-%d")
    return [date_formatted]


class DateAdder(object):
    """ returns Date of service """
    main()


class RoleNameAdder(object):
    """ Map a target field based on a controlley vocab field 
    
    This is the opposite of a rule translator. The values which define the 
    correct source key come from a controlled vocabulary field of a dv metadata
    block. 
    
    Examples: Contributor - Role & Name
    """

    def __init__(self):
        self.values = {}
        #TODO: shoud be moved to config file
        self.template = """{{familyName}}{{#givenName}}, {{givenName}}{{/givenName}}
                           {{^familyName}}{{name}}{{/familyName}}"""

    def main(self, source_key, target_key, source_key_values, t_key):
        """ Return the value of *t_key* 
        
        The input values are expected to be a dict of lists, with the keys being
        the values of the role field (2nd field in target).
        The special key 'norole' simply doesn't set the role value.
        The name values are construced accurding to the specified template.
        """
        if t_key in self.values:
            return self.values[t_key]
        else:
            self.values = {key: [] for key in target_key}
            for s_key in source_key:
                s_key_values = source_key_values.get(s_key, {})
                # s_key_values = {"norole": [{}, {}, {}]} # num elems contributor 
                if len(s_key_values) > 0 and len(list(s_key_values.values())[0]) > 0:
                    role = s_key.split("#")[0]
                    values = [chevron.render(self.template, data) for data in s_key_values[role]]
                    self.values[target_key[0]].extend([v.strip() for v in values])
                    if role == 'norole':
                        self.values[target_key[-1]].extend(['none' for _ in values])
                    else:
                        self.values[target_key[-1]].extend([role for _ in values])
            return self.values[t_key]


class IdentifierAdder(object):
    """ Splits a source field based on dv identifier scheme field
    
    Works for authorIdentifierScheme, but can be extended.
    """

    def __init__(self):
        self.values = {}

    def main(self, source_key, target_key, source_key_values, t_key):
        if t_key in self.values:
            return self.values[t_key]
        else:
            self.values = {key: [] for key in target_key}
            contr_vocab = DV_FIELD[target_key[-1]].controlled_vocabulary
            source_key = [source_key] if not isinstance(source_key, list) else source_key
            for s_key in source_key:
                s_key_values = source_key_values.get(s_key, [])
                # e.g., s_key_values = ["https://orcid.org/0000-0001-8188-620X", "https://d-nb.info/gnd/143233165"]
                if len(s_key_values) > 0:
                    for s_key_value in s_key_values:
                        scheme = None
                        for voc in contr_vocab:
                            if voc.lower() in s_key_value.lower():
                                scheme = voc
                                break
                        if scheme is None:
                            self.values[target_key[-1]].append('none')
                            self.values[target_key[0]].append('none')
                            continue
                        self.values[target_key[-1]].append(scheme)
                        # this needs to be more sophisticated to match further cases
                        self.values[target_key[0]].append(s_key_value.split("/")[-1])
            return self.values[t_key]
