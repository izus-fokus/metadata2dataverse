import yaml
import os
from flask import Flask, request, abort, jsonify, g
from validators import length

from api.globals import MAPPINGS, DV_FIELD, DV_MB, DV_CHILDREN, DV_FIELD_ZENODO
from api.resources import read_all_config_files, read_all_scheme_files, read_config, fill_MAPPINGS, read_zenodo_scheme
from models.ReaderFactory import ReaderFactory
from models.MetadataModel import (MultipleVocabularyField, VocabularyField, CreateDatasetSchema, CreateDataset,
                                  DatasetSchema, MetadataBlock, Dataset, EditFormat, EditScheme, PrimitiveField,
                                  CompoundField, MultipleCompoundField, MultiplePrimitiveField)
from builtins import isinstance
import json


def create_app():
    # create and configure the app
    app = Flask(__name__)

    with app.app_context():
        read_zenodo_scheme()
        read_all_scheme_files()
        read_all_config_files()

    @app.errorhandler(400)
    def format_missing(scheme):
        return jsonify(
            message="{} scheme exists in different formats. Check resource `/mapping` for available schemes/formats and "
                    "specify formatSetting in your request.".format(
                scheme)), 400

    @app.errorhandler(404)
    def resource_not_found(scheme):
        return jsonify(
            message="{} mapping schema does not exist. Check resource `/mapping` for available schemes.".format(scheme)), 404

    @app.errorhandler(409)
    def already_exists(scheme_and_format):
        return jsonify(message="{} mapping scheme already exists. Use PUT to change it.".format(scheme_and_format)), 409

    @app.errorhandler(415)
    def unsupported_type(scheme):
        return jsonify(
            message="{} does not support requested media type. Check resource `/mapping/` for available media types of "
                    "this metadata scheme.".format(
                scheme)), 415

    @app.errorhandler(422)
    def error_yaml(warnings):
        return jsonify(message="{}".format(warnings)), 422

    @app.errorhandler(500)
    def error_yaml_server(warnings):
        return jsonify(
            message="Mapping is not correctly configured. Please contact the administrators at fokus@izus.uni-stuttgart.de "
                    "and transmit the following information: {}.".format(
                warnings)), 500

    def removeConfigFile(scheme, formatSetting=None):
        rootdir = './resources/config'
        for subdir, dirs, files in os.walk(rootdir):
            for file in files:
                path = os.path.join(subdir, file)
                open_yaml_file = open(path)
                config = read_config(open_yaml_file)
                open_yaml_file.close()
                if config.scheme == scheme and (formatSetting is None or config.format == formatSetting):
                    os.remove(path)

    def verbosize(response):
        return {'success': True, 'warnings': g.warnings, 'response': response}

    def get_mapping(scheme, formatSetting=None):
        """ Returns config (mapping) from MAPPINGS dictionary with scheme as key.

        If scheme is not in MAPPINGS: abort
        If formatSetting is not specified and only one mapping for scheme available: return this mapping
        Elif: return mapping with specified scheme and formatSetting

        Parameters
        ----------
        scheme : str
        formatSetting : str

        Returns
        ----------
        mapping : Config obj
        """
        mappings = MAPPINGS.get(scheme)
        # scheme does not exist
        if mappings is None:
            abort(404, scheme)
        if formatSetting is None and len(mappings) == 1:
            return mappings[0]
        for mapping in mappings:
            if mapping.format == formatSetting:
                return mapping
        # formatSetting does not exist
        abort(400, scheme)

    def translate_source_keys(source_key_values, mapping):
        """ Translates Source Keys to Target Keys with corresponding values (values unchanged).

        Rules and priorities from mapping get applied.

        Parameters
        ---------
        source_key_values : dict (key: source_key, value: values)
        mapping : Config obj

        Returns
        ---------
        target_key_values : dict (key: target_key, value: values)
        """
        target_key_values = {}
        # check if rules can be applied to source_keys
        source_keys_to_delete = []
        for k, v in source_key_values.items():
            if k in mapping.rules_dict:
                rule = mapping.rules_dict.get(k)
                for value in v:
                    if value in rule:
                        translators = rule.get(value)
                        for translator in translators:
                            target_key = translator.target_key
                            priority = translator.priority
                            source_keys_to_delete.append(translator.source_key)
                            source_keys_to_delete.append(k)
                            value_new = translator.get_value(source_key_values)

                            if value_new is not None:
                                if target_key in target_key_values:
                                    if priority > target_key_values[target_key][1]:
                                        target_key_values[target_key] = [value_new, priority]
                                else:
                                    target_key_values[target_key] = [value_new, priority]
        # delete used source_keys
        for key in source_keys_to_delete:
            source_key_values.pop(key, None)
        for k, v in source_key_values.items():
            is_list = False
            translators = mapping.get_translator(k)
            if translators is None:
                continue
            for translator in translators:
                target_key = translator.target_key
                if isinstance(target_key, list):
                    is_list = True
                else:
                    target_key = [target_key]
                priority = translator.get_priority()
                for t_key in target_key:
                    if is_list:
                        value = translator.get_value(source_key_values, t_key=t_key)
                    else:
                        value = translator.get_value(source_key_values)
                    if t_key in target_key_values:
                        existing_value, existing_priority = target_key_values[t_key]

                        if priority > existing_priority:
                            # Check if the existing value is a list
                            if isinstance(existing_value, list) and isinstance(value, list):
                                # Update only if the new value is not 'none'
                                for e in range(len(existing_value)):
                                    if e < len(value):
                                        if value[e] != 'None':
                                            target_key_values[t_key][0][e] = value[e]
                                            target_key_values[t_key][1] = priority


                            else:
                                target_key_values[t_key] = [value, priority]

                    else:
                        target_key_values[t_key] = [value, priority]

        #                if k in mapping.addition_translators_dict:
        #                    is_list = False
        #
        #                    translator = mapping.addition_translators_dict.get(k)
        #                    target_key = translator.target_key
        #                    if isinstance(target_key, list):
        #                        is_list = True
        #                    else:
        #                        target_key = [target_key]
        #                    for t_key in target_key:
        #                        if is_list:
        #                            value = translator.get_value(source_key_values, t_key=t_key)
        #                        else:
        #                            value = translator.get_value(source_key_values)
        #                        priority = translator.priority
        #                        if t_key in target_key_values:
        #                            #TODO: if value is list: do not overwrite with 'none', instead use old value
        #                            if priority > target_key_values[t_key][1]:
        #                                target_key_values[t_key] = [value,priority]
        #                        else:
        #                            target_key_values[t_key] = [value,priority]
        # print("\n target key values:", (json.dumps(target_key_values, indent=4)))
        # delete priorities
        for k, v in target_key_values.items():
            target_key_values[k].pop()
            target_key_values[k] = v[0]
        return target_key_values

    # def translate_source_keys_zenodo(source_key_values, mapping):
    #     """ Translates Source Keys to Target Keys with corresponding values (values unchanged).
    #
    #     Rules and priorities from mapping get applied.
    #
    #     Parameters
    #     ---------
    #     source_key_values : dict (key: source_key, value: values)
    #     mapping : Config obj
    #
    #     Returns
    #     ---------
    #     target_key_values : dict (key: target_key, value: values)
    #     """
    #     target_key_values = {}
    #     # check if rules can be applied to source_keys
    #     source_keys_to_delete = []
    #     for k, v in source_key_values.items():
    #         if k in mapping.rules_dict:
    #             rule = mapping.rules_dict.get(k)
    #             for value in v:
    #                 if value in rule:
    #                     translators = rule.get(value)
    #                     for translator in translators:
    #                         target_key = translator.target_key
    #                         priority = translator.priority
    #                         source_keys_to_delete.append(translator.source_key)
    #                         source_keys_to_delete.append(k)
    #                         value_new = translator.get_value(source_key_values)
    #
    #                         if value_new is not None:
    #                             if target_key in target_key_values:
    #                                 if priority > target_key_values[target_key][1]:
    #                                     target_key_values[target_key] = [value_new, priority]
    #                             else:
    #                                 target_key_values[target_key] = [value_new, priority]
    #     # delete used source_keys
    #     for key in source_keys_to_delete:
    #         source_key_values.pop(key, None)
    #     for k, v in source_key_values.items():
    #         is_list = False
    #         translators = mapping.get_translator(k)
    #         if translators is None:
    #             continue
    #         for translator in translators:
    #             target_key = translator.target_key
    #             if isinstance(target_key, list):
    #                 is_list = True
    #             else:
    #                 target_key = [target_key]
    #             priority = translator.get_priority()
    #             for t_key in target_key:
    #                 if is_list:
    #                     value = translator.get_value(source_key_values, t_key=t_key)
    #                 else:
    #                     value = translator.get_value(source_key_values)
    #                 if t_key in target_key_values:
    #                     existing_value, existing_priority = target_key_values[t_key]
    #
    #                     if priority > existing_priority:
    #                         # Check if the existing value is a list
    #                         if isinstance(existing_value, list) and isinstance(value, list):
    #                             # Update only if the new value is not 'none'
    #                             for e in range(len(existing_value)):
    #                                 if e < len(value):
    #                                     if value[e] != 'None':
    #                                         target_key_values[t_key][0][e] = value[e]
    #                                         target_key_values[t_key][1] = priority
    #
    #
    #                         else:
    #                             target_key_values[t_key] = [value, priority]
    #
    #                 else:
    #                     target_key_values[t_key] = [value, priority]
    #
    #     for k, v in target_key_values.items():
    #         target_key_values[k].pop()
    #         target_key_values[k] = v[0]
    #     return target_key_values

    def get_p_field(type_class, k, v, multiple, field):
        """ Checks type_class of field and triggers get_primitive_field() or get_vocabulary_field() methods.

        Parameters
        ---------
        type_class : str
        k : str
        v : list
        multiple : Boolean
        field : Field obj

        Returns
        ---------
        p_field : Field obj (from MetadataModel)
        """
        # Primitive
        if type_class == "primitive":
            p_field = get_primitive_field(k, v, multiple)
            return p_field
        # Controlled Vocabulary
        if type_class == "controlled_vocabulary":
            if v == "":  # special case for getEmptyDataverseJson
                p_field = get_vocabulary_field(k, [""], multiple)
                return p_field
            v_checked = field.check_controlled_vocabulary(v)
            if len(v_checked) > 0:  # v did match controlled vocab
                p_field = get_vocabulary_field(k, v_checked, multiple)
                return p_field
            else:  # v did not match controlled vocab
                p_field = get_vocabulary_field(k, ['none'], multiple)
                return p_field
        return None

    def get_p_field_zenodo(type_class, k, v, multiple, field):
        """ Checks type_class of field and triggers get_primitive_field() or get_vocabulary_field() methods.

        Parameters
        ---------
        type_class : str
        k : str
        v : list
        multiple : Boolean
        field : Field obj

        Returns
        ---------
        p_field : Field obj (from MetadataModel)
        """
        # Primitive
        if type_class == "primitive":
            p_field = get_primitive_field(k, v, multiple)
            return p_field
        # Controlled Vocabulary
        if type_class == "controlled_vocabulary":
            if v == "":  # special case for getEmptyDataverseJson
                p_field = get_vocabulary_field(k, [""], multiple)
                return p_field
            v_checked = field.check_controlled_vocabulary(v)
            if len(v_checked) > 0:  # v did match controlled vocab
                p_field = get_vocabulary_field(k, v_checked, multiple)
                return p_field
            else:  # v did not match controlled vocab
                p_field = get_vocabulary_field(k, ['none'], multiple)
                return p_field
        return None

    def get_primitive_field(k, v, multiple):
        """ Method for generating primitive Field obj from MetadataModel class.

        If target key is multiple: merge all values from v (skip None values)
        If target key is not multiple: only one value allowed in v (skip None values)

        Parameters
        ---------
        k : str
        v : list
        multiple : Boolean

        Return
        ---------
        p_field : MultiplePrimitiveField obj or PrimitiveField obj
        """
        if multiple:
            v_new = []
            for value in v:
                if value is not None:
                    v_new.append(value)
            v = v_new
            p_field = MultiplePrimitiveField(k, v)
            return p_field
        if not multiple:
            v_new = ""
            counter = 0
            for value in v:
                if value is not None:
                    counter += 1
                    if counter == 1:
                        v_new += value
                    elif value != 'none':
                        g.warnings.append(
                            k + " has only one allowed value. We deleted value number " + str(counter) + ": " + value)
            v = v_new
            p_field = PrimitiveField(k, v)

            return p_field
        return None

    def get_vocabulary_field(k, v, multiple):
        """ Method for generating vocabulary Field obj from MetadataModel class.

        Parameters
        ---------
        k : str
        v : list
        multiple : Boolean

        Return
        ---------
        p_field : MultipleVocabularyField or VocabularyField obj
        """
        if multiple:
            # if not isinstance(v, list):
            #     v = [v]
            v_field = MultipleVocabularyField(k, v)
            return v_field
        if not multiple:
            if isinstance(v, list):
                v = ", ".join(v)
            v_field = VocabularyField(k, v)
            return v_field
        return None

    def get_compound_field(parent):
        """ Method for generating compound Field obj from MetadataModel class.

        If parent is multiple: generates MultipleCompoundFied
        Else: generates CompoundField

        Parameters
        ---------
        parent : str
        # k : str
        # v : list
        # multiple : Boolean

        Return
        ---------
        c_field : MultipleCompoundFied obj or CompoundField obj
        """
        parent_field = DV_FIELD.get(parent)
        parent_field_multiple = parent_field.multiple
        if parent_field_multiple:
            c_field = MultipleCompoundField(parent)
            return c_field
        if not parent_field_multiple:
            c_field = CompoundField(parent)
            return c_field

        return None

    def get_compound_field_zenodo(parent):
        """ Method for generating compound Field obj from MetadataModel class.

        If parent is multiple: generates MultipleCompoundFied
        Else: generates CompoundField

        Parameters
        ---------
        parent : str
        # k : str
        # v : list
        # multiple : Boolean

        Return
        ---------
        c_field : MultipleCompoundFied obj or CompoundField obj
        """
        parent_field = DV_FIELD.get(parent)
        parent_field_multiple = parent_field.multiple
        if parent_field_multiple:
            c_field = MultipleCompoundField(parent)
            return c_field
        if not parent_field_multiple:
            c_field = CompoundField(parent)
            return c_field

        return None

    def build_json(target_key_values, method):
        """ Builds complete and nested json output which is DataVerse compatible.

        Parameters
        ---------
        target_key_values : dict
        method : str

        Returns
        ---------
        if method = 'update'
        Dataset obj (MetadataModel)

        if method = 'edit'
        EditFormat obj (MetadataModel)

        if method = 'create'
        CreateDataset obj (MetadataModel)
        """
        number_of_values = 0
        json_result = EditFormat()
        parents_dict = {}
        children_dict = {}
        mb_dict = {}
        # fill children_dict with target_key (key) and p_fields (value)
        # fill parents_dict with parent_key (key) and c_fields (value)
        # or fill mb_dict and json_result directly with no-parent-keys
        for k, v in target_key_values.items():
            field = DV_FIELD.get(k)
            if field is None:
                g.warnings.append("Field {} not in Dataverse-configuration. Check your YAML file.".format(k))
                continue
            parent = field.parent
            type_class = field.type_class
            multiple = field.multiple
            mb_id = field.metadata_block
            if not field.check_value(v):
                g.warnings.append(
                    "Wrong formatSetting of {}, this field should be a {}. {} field removed".format(k, field.field_type, k))
                continue

            if mb_id not in mb_dict:
                mb = MetadataBlock(mb_id, DV_MB[mb_id])
                mb_dict[mb_id] = mb
            # has parent
            if parent is not None:
                c_field = get_compound_field(parent)
                # MultipleCompoundField
                if isinstance(c_field, MultipleCompoundField):
                    children_dict[k] = []
                    if isinstance(v, list):
                        for value in v:
                            p_field = get_p_field(type_class, k, [value], multiple, field)
                            if p_field is not None:
                                children_dict[k].append(p_field)
                    else:
                        p_field = get_p_field(type_class, k, v, multiple, field)
                        if p_field is not None:
                            children_dict[k].append(p_field)
                # CompoundField
                if isinstance(c_field, CompoundField):
                    # PrimitiveFields
                    children_dict[k] = get_p_field(type_class, k, v, multiple, field)
                parents_dict[parent] = c_field
            # has no parent
            if parent is None:
                p_field = get_p_field(type_class, k, v, multiple, field)
                if p_field is not None and p_field.value != ['none'] and p_field.value != 'none':
                    mb_dict[mb_id].add_field(p_field)
                    json_result.add_field(p_field)
        # build compound fields
        for parent, c_field_outer in parents_dict.items():
            mb_id = DV_FIELD.get(parent).metadata_block
            children = DV_CHILDREN.get(parent)
            if isinstance(c_field_outer, MultipleCompoundField):
                for child in children:
                    if child in children_dict:
                        number_of_values = len(children_dict.get(child))
                        break
                for i in range(number_of_values):
                    c_field_inner = CompoundField(parent)
                    for child in children:
                        if child in children_dict:
                            if i < len(children_dict[child]):
                                p_field = children_dict.get(child)[i]
                                if p_field is not None and p_field.value != [
                                    'none'] and p_field.value != 'none' and p_field.value != [] and p_field.value.strip() != '':
                                    c_field_inner.add_value(p_field, child)
                                else:
                                    continue
                    if bool(c_field_inner.value):
                        c_field_outer.add_value(c_field_inner)
                json_result.add_field(c_field_outer)
                mb_dict[mb_id].add_field(c_field_outer)
            else:
                for child in children:
                    if child in children_dict:
                        p_field = children_dict.get(child)
                        if p_field is not None and p_field.value != [
                            'none'] and p_field.value != 'none' and p_field.value.strip() != '':
                            c_field_outer.add_value(p_field, child)
                json_result.add_field(c_field_outer)
                mb_dict[mb_id].add_field(c_field_outer)
        if method == 'update':
            dataset = Dataset()
            for mb_id, block in mb_dict.items():
                dataset.add_block(mb_id, block)
            return dataset
        if method == 'edit':
            return json_result
        if method == 'create':
            dataset = Dataset()
            for mb_id, block in mb_dict.items():
                dataset.add_block(mb_id, block)
            create_dataset = CreateDataset(dataset)
            return create_dataset
        return None

    def build_json_zenodo(target_key_values, method):
        """ Builds complete and nested json output which is Zenodo compatible.

        Parameters
        ---------
        target_key_values : dict
        method : str

        Returns
        ---------
        if method = 'update'
        Dataset obj (MetadataModel)

        if method = 'edit'
        EditFormat obj (MetadataModel)

        if method = 'create'
        CreateDataset obj (MetadataModel)
        """
        number_of_values = 0
        json_result = {"data": { "attributes" : {} }}
        parents_dict = {}
        children_dict = {}
        mb_dict = {}
        # fill children_dict with target_key (key) and p_fields (value)
        # fill parents_dict with parent_key (key) and c_fields (value)
        # or fill mb_dict and json_result directly with no-parent-keys
        for k, v in target_key_values.items():
            field = DV_FIELD_ZENODO.get(k)
            if field is None:
                g.warnings.append("Field {} not in Zenodo-configuration. Check your YAML file.".format(k))
                continue
            json_result["data"]["attributes"].update(contruct_zenodo_element(k,v))
        if method == 'update':
            dataset = Dataset()
            for mb_id, block in mb_dict.items():
                dataset.add_block(mb_id, block)
            return dataset
        if method == 'edit':
            return json_result
        if method == 'create':
            dataset = Dataset()
            for mb_id, block in mb_dict.items():
                dataset.add_block(mb_id, block)
            create_dataset = CreateDataset(dataset)
            return create_dataset
        return None

    def contruct_zenodo_element(k: str, v: str):
        fieldparts = k[2:].split("/")
        oldParts = []
        constructedJSON = {}
        for part in fieldparts:
            if part == "0":
                value = []
                oldParts.append(value)
            else:
                value = part
                oldParts.append(value)
        constructedJSON[oldParts[0]] = []
        for oldPart in range(len(oldParts)):
            if oldPart < (len(oldParts)):
                if oldPart == 0 or len(oldParts[oldPart]) == 0:
                    continue
                else:
                    add = {oldParts[oldPart] : {v[0]}}
                    constructedJSON[oldParts[oldPart-2]].append(add)
        return constructedJSON


    @app.route('/metadata/<string:scheme>', methods=["POST"])
    def mapMetadata(scheme):
        """Fills a Dataverse compatible JSON template with all mappable values from the input metadata.

        Requires the mapping for scheme and content_type of request to exist.

        Parameters
        ----------
        scheme : str

        Returns
        ----------
        response : json
        """
        response = ""
        method = request.args.get('method', type=str, default='update')
        verbose = request.args.get('verbose', type=bool, default=False)
        g.warnings = []
        # get mapping for requested scheme
        mapping = get_mapping(scheme, request.content_type)
        # read input depending on content-type and get all key-value-pairs in input
        reader = ReaderFactory.create_reader(request.content_type)
        if reader is None:
            abort(415, scheme)
        # translate key-value-pairs in input to target scheme
        source_key_values = reader.read(request.data, mapping)
        target_key_values = translate_source_keys(source_key_values, mapping)
        # resp_url = check_value("Geeksoreeks1", "text")     testing text

        # build json out of target_key_values and DV_FIELDS, DV_MB, DV_CHILDREN
        if mapping.get_scheme() == "zenodo":
            result = build_json_zenodo(target_key_values, method)
            if method == 'edit':
                response = result
            elif method == 'update':
                response = result
            elif method == 'create':
                response = result
            if verbose:
                response = verbosize(response)
                return jsonify(response), 202
            else:
                return jsonify(response), 200
        else:
            result = build_json(target_key_values, method)
            if method == 'edit':
                response = EditScheme().dump(result)
            elif method == 'update':
                response = DatasetSchema().dump(result)
            elif method == 'create':
                response = CreateDatasetSchema().dump(result)
            if verbose:
                response = verbosize(response)
                return jsonify(response), 202
            else:
                return jsonify(response), 200


    @app.route('/metadata/<string:scheme>')
    def getEmptyDataverseJson(scheme):
        """ Returns an empty JSON template for Dataverse with all mappable fieldsElement of the input metadata scheme.

        Requires the mapping for scheme to exist.

        Parameters
        ----------
        scheme : str

        Returns
        ----------
        response : json
        """
        method = request.args.get('method', type=str, default='update')
        verbose = request.args.get('verbose', type=bool, default=False)

        g.warnings = []
        response = ""
        # get all target keys from scheme
        try:
            mapping = MAPPINGS.get(scheme)[0]
        except IndexError as e:
            abort(404, scheme, e.__str__())
        target_keys = mapping.get_target_keys()
        # build empty target key dictionary
        target_key_values = dict.fromkeys(target_keys, "")
        if mapping.get_scheme() == "zenodo":
            result = build_json_zenodo(target_key_values, method)
            if method == 'edit':
                response = result
            elif method == 'update':
                response = result
            elif method == 'create':
                response = result
            if verbose:
                response = verbosize(response)
                return jsonify(response), 202
            else:
                return jsonify(response), 200
        else:
            result = build_json(target_key_values, method)
            if method == 'edit':
                response = EditScheme().dump(result)
            elif method == 'update':
                response = DatasetSchema().dump(result)
            elif method == 'create':
                response = CreateDatasetSchema().dump(result)
            if verbose:
                response = verbosize(response)
                return jsonify(response), 202
            else:
                return jsonify(response), 200


    @app.route('/mapping', methods=["GET"])
    def SchemasMappingInfo():
        """ Returns a general overview of existing mappings and formats. """
        list_of_mappings = []
        for m in MAPPINGS:
            for mapping in MAPPINGS[m]:
                list_of_mappings.append(mapping.dump())
        return jsonify(list_of_mappings)

    @app.route('/mapping/<string:scheme>', methods=["GET"])
    def getSchemeMapping(scheme):
        """ Returns a mapping file for scheme.
        If the scheme exists in several formats the query parameter has to be given.
        """
        formatSetting = request.args.get('formatSetting', default=None)
        mapping = get_mapping(scheme, formatSetting)
        return mapping.pretty_yaml()

    @app.route('/mapping', methods=["POST"])
    def createSchemaMapping():
        """ Adds a new mapping. Aborts if target keys do not exist in DV_FIELDS. """
        new_mapping = request.data
        config = read_config(new_mapping)
        # check if yaml file was correct
        if len(g.warnings) > 0:
            warnings = ' '.join(g.warnings)
            abort(422, warnings)
        fill_MAPPINGS(config)
        if len(g.warnings) > 0:
            warnings = ' '.join(g.warnings)
            abort(422, warnings)
        with open("./resources/config/{}_{}.yml".format(config.scheme, config.format), "w") as f:
            yaml.dump(yaml.safe_load(new_mapping), f)
        response = {'success': True, 'created': config.scheme, 'location': '/mapping/{}'.format(config.scheme)}
        return jsonify(response), 201

    @app.route('/mapping/<string:scheme>', methods=["PUT"])
    def editSchemeMapping(scheme):
        """ Change an existing mapping configuration. Aborts if target keys do not exist in DV_FIELDS.

        Parameters
        ---------
        scheme : str

        Returns
        ---------
        response : json
        """
        formatSetting = request.args.get('formatSetting', default=None)
        new_mapping = request.data
        try:
            mappings = MAPPINGS[scheme]
        except IndexError as e:
            abort(404, scheme, e.__str__())  # no existing mappings for scheme found

        config = read_config(new_mapping)
        if len(g.warnings) > 0:
            warnings = ' '.join(g.warnings)
            abort(422, warnings)  # wrong values in yaml file

        if formatSetting is None:
            formatSetting = config.format
        if config.scheme == scheme:
            for mapping in mappings:
                if mapping.format == formatSetting:  # success
                    mappings.remove(mapping)
                    MAPPINGS[scheme] = mappings
                    fill_MAPPINGS(config)
                    removeConfigFile(scheme, formatSetting)
                    with open("./resources/config/{}_{}.yml".format(config.scheme, config.format), "w") as f:
                        yaml.dump(yaml.safe_load(new_mapping), f)
                    response = {'success': True, 'updated': scheme}
                    return jsonify(response), 204
            abort(400, scheme)  # no mapping with the formatSetting found
        else:
            abort(400, scheme)  # formatSetting/scheme in new yaml file does not correspond to the specified scheme/formatSetting

    @app.route('/mapping/<string:scheme>', methods=["DELETE"])
    def deleteSchemeMapping(scheme):
        """ Deletes a mapping for a metadata scheme. Fails if scheme or formatSetting not found.

        Parameters
        ---------
        scheme : str

        Returns
        ---------
        response : json
        """
        formatSetting = request.args.get('formatSetting', default=None)
        try:
            mappings = MAPPINGS[scheme]
        except IndexError as e:
            abort(404, scheme, e.__str__())

        if len(mappings) > 1:
            # there is more than one mapping of the same scheme
            formats = []
            for mapping in mappings:
                formats.append(mapping.format)
                if formatSetting is not None:
                    if mapping.format == formatSetting:
                        mappings.remove(mapping)
                        removeConfigFile(scheme, formatSetting)
            MAPPINGS[scheme] = mappings

            if formatSetting is None:
                abort(422,
                      "The scheme '{}' is defined for {} different file formats:{}. Please specify the formatSetting to be "
                      "deleted.".format(
                          scheme, len(mappings), ", ".join(formats)))
            elif formatSetting not in formats:
                abort(400, "The formatSetting {} does not match with the formatSetting of scheme {}".format(formatSetting, scheme))

        else:
            mapping = mappings[0]
            if formatSetting is not None and mapping.format != formatSetting:
                abort(400, "The formatSetting {} does not match with the formatSetting of scheme {}".format(formatSetting, scheme))
            MAPPINGS[scheme] = []
            removeConfigFile(scheme)

        response = {'success': True, 'deleted': scheme}
        return jsonify(response), 204

    @app.route('/dv-metadata-config', methods=["GET"])
    def getMetadataBlocks():
        """ Returns available metadata blocks.

        Returns
        --------
        DV_MB : json
        """
        return jsonify(DV_MB)

    @app.route('/reading-config', methods=["GET"])
    def readingconfig():
        try:
            read_all_scheme_files()
            read_all_config_files()

            response = {"reading config": "done"}
            return jsonify(response), 200

        except BaseException as e:
            response = {"reading config failed": e.__str__()}
            return jsonify(response), 400

    return app
