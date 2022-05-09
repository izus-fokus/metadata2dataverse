from flask import Flask, request, abort, jsonify, send_file, g
from api.globals import MAPPINGS, DV_FIELD, DV_MB, DV_CHILDREN
from api.resources import read_all_config_files, read_all_scheme_files, read_config, fill_MAPPINGS
from models.ReaderFactory import ReaderFactory
from models.Translator import MergeTranslator, AdditionTranslator
from models.MetadataModel import MultipleVocabularyField, VocabularyField, CreateDatasetSchema, CreateDataset, DatasetSchema, MetadataBlock, MetadataBlockSchema, Dataset, EditFormat, EditScheme, PrimitiveField, CompoundField, MultipleCompoundField, MultiplePrimitiveField, PrimitiveFieldScheme, CompoundFieldScheme, MultipleCompoundFieldScheme, MultiplePrimitiveFieldScheme
from builtins import isinstance
from datetime import datetime
import yaml
import validators #for checking url and email 
import re #for checking text

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
        
        
    # helper functions
    @app.before_first_request
    def init_globals():
        read_all_scheme_files()
        read_all_config_files()
        
    @app.errorhandler(400)
    def format_missing(scheme):
        return jsonify(message="{} scheme exists in different formats. Check resource `/mapping` for available schemes/formats and specify format in your request.".format(scheme)), 400    
    @app.errorhandler(404)
    def resource_not_found(scheme):
        return jsonify(message="{} mapping schema does not exist. Check resource `/mapping` for available schemes.".format(scheme)), 404    
    @app.errorhandler(409)
    def already_exists(scheme_and_format):
        return jsonify(message="{} mapping scheme already exists. Use PUT to change it.".format(scheme_and_format)), 409        
    @app.errorhandler(415)
    def unsupported_type(scheme):
        return jsonify(message="{} does not support requested media type. Check resource `/mapping/{}` for available media types of this metadata scheme.".format(scheme)), 415
    @app.errorhandler(422)
    def error_yaml(warnings):
        return jsonify(message="{}".format(warnings)), 422
    @app.errorhandler(500)
    def error_yaml_server(warnings):
        return jsonify(message="Mapping is not correctly configured. Please contact the administrators at fokus@izus.uni-stuttgart.de and transmit the following information: {}.".format(warnings)), 500
            
        
    def verbosize(response):
        return {'success': True,
                'warnings': g.warnings,
                'response': response}


    def gen_message(warnings):
        return '. '.join(warnings)

    def isAllPresent(str):
        # ReGex to check if a string                        # I think this is not what "text" fieldtype says, it wants any text, so can we just check this with None?
        # contains uppercase, lowercase
        # special character & numeric value
        
        regex = ("^(?=.*[a-z])(?=." +
             "*[A-Z])(?=.*\\d)" +
             "(?=.*[-+_!@#$%^&*., ?]).+$")
        
        #Compile the ReGex
        p = re.compile(regex)
        
        # If the string is empty
        # return false
        if (str == None):
            #print("No")
            text_valid = 0
            return text_valid
            
            # Print Yes if string
            # matches ReGex
        
        if(re.search(p, str)):
            #print("Yes")
            text_valid = 1     
        else:
            #print("No")
            text_valid = 0
        
        return text_valid 
    
    def check_value(value, fieldtype): #This function checks if value of a field type is valid or not? 
        #print(value)
        #print("aboveme")
        if fieldtype == "url":
            if validators.url(value):
                valid = 1
                #print("passed and valid")
                
                #for keys, values in DV_FIELD.items():         ##For viewing field type of diff fields in DV_FIELD dictionary
                #    print(keys)

            else: 
                valid = 0
                #print("invalid will be removed")     
        
        elif fieldtype == "email":
            if validators.email(value):
                valid = 1
            else:
                valid = 0

        elif fieldtype == "date":
            format_d = "%d-%m-%Y"
            try:
                res = bool(datetime.strptime(value, format))
                valid = 1
            except ValueError:
                    res=False    
                    valid = 0

        elif fieldtype == "int":
            check_int = isinstance(value, int)
            if check_int == True:
                valid = 1
            else:
                valid = 0

        elif fieldtype == "float":
            check_float = isinstance(value, float)
            if check_float == True:
                valid = 1
            else:
                valid = 0

        elif fieldtype == "none":
            if value is None:
                valid = 1
            else:
                valid = 0

        elif fieldtype == "text":
            check_text = isAllPresent(value)
            if check_text == 1:
                valid = 1
            else:
                valid = 0

        return valid        
        

    
    def get_mapping(scheme,format=None):
        """ Returns config (mapping) from MAPPINGS dictionary with scheme as key.
        
        If scheme is not in MAPPINGS: abort
        If format is not specified and only one mapping for scheme available: return this mapping
        Elif: return mapping with specified scheme and format     
        
        Parameters
        ----------
        scheme : str
        format : str        
        
        Returns
        ----------
        mapping : Config obj
        """
        mappings = MAPPINGS.get(scheme)        
        # scheme does not exist
        if mappings is None:
            abort(404, scheme)
        if format == None and len(mappings)==1:
            return mappings[0]
        for mapping in mappings:
            if mapping.format == format:
                return mapping
        # format does not exist
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
        for k,v in source_key_values.items():     
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
                            if value_new != None:   
                                if target_key in target_key_values:             
                                    if priority > target_key_values[target_key][1]:
                                        target_key_values[target_key] = [value_new,priority]
                                else:
                                    target_key_values[target_key] = [value_new,priority]                                    
        # delete used source_keys                        
        for key in source_keys_to_delete:
            source_key_values.pop(key, None)        
        for k,v in source_key_values.items():  
            translator = mapping.get_translator(k)
            if translator == None:
                continue
            target_key = translator.target_key
            priority = translator.get_priority()
            value = translator.get_value(source_key_values)     
            if target_key in target_key_values:                
                if priority > target_key_values[target_key][1]:
                    target_key_values[target_key] = [value,priority]
            else:
                target_key_values[target_key] = [value,priority] 
            if k in mapping.addition_translators_dict:
                translator = mapping.addition_translators_dict.get(k)
                target_key = translator.target_key 
                value = translator.get_value()
                priority = translator.priority 
                if target_key in target_key_values:                
                    if priority > target_key_values[target_key][1]:
                        target_key_values[target_key] = [value,priority]
                else:
                    target_key_values[target_key] = [value,priority] 
        # delete priorities
        for k,v in target_key_values.items():
            target_key_values[k].pop()        
            target_key_values[k] = v[0]       
        return target_key_values
    
    
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
            p_field = get_primitive_field(k,v,multiple)
            return p_field
        # Controlled Vocabulary
        if type_class == "controlled_vocabulary":
            if v == "":        # special case for getEmptyDataverseJson
                p_field = get_vocabulary_field(k, v, multiple)
                return p_field
            v_checked = field.check_controlled_vocabulary(v)
            if len(v_checked) > 0:  # v did match controlled vocab
                p_field = get_vocabulary_field(k, v_checked, multiple)   
                return p_field             
            else:                   # v did not match controlled vocab
                p_field = get_vocabulary_field(k, ['none'], multiple)   
                return p_field   
            
            
    def get_primitive_field(k,v,multiple):       
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
        if multiple == True:
            v_new = []
            for value in v:
                if value != None:
                    v_new.append(value)
            v = v_new
            p_field = MultiplePrimitiveField(k,v)
        if multiple == False:        
            v_new = ""
            counter = 0
            for value in v:
                if value != None:
                    counter += 1
                    if counter == 1:
                        v_new += value
                    elif value != 'none':
                        g.warnings.append(k + " has only one allowed value. We deleted value number " + str(counter) + ": " + value)
            v = v_new
            p_field = PrimitiveField(k,v)
        return p_field
    
    
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
        if multiple == True:
            if not isinstance(v,list):
                v = [v]
            v_field = MultipleVocabularyField(k,v)
        if multiple == False:
            if isinstance(v,list):
                v = ", ".join(v)
            v_field = VocabularyField(k,v)   
        return v_field
    
    
    def get_compound_field(parent,k,v,multiple):
        """ Method for generating compound Field obj from MetadataModel class.
        
        If parent is multiple: generates MultipleCompoundFied
        Else: generates CompoundField
        
        Parameters
        ---------
        parent : str
        k : str
        v : list
        multiple : Boolean
        
        Return
        ---------
        c_field : MultipleCompoundFied obj or CompoundField obj        
        """
        parent_field = DV_FIELD.get(parent)
        parent_field_multiple = parent_field.multiple
        if parent_field_multiple == True:
            c_field = MultipleCompoundField(parent)
        if parent_field_multiple == False:
            c_field = CompoundField(parent)    
        return c_field    
    
    
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
        json_result = EditFormat() 
        parents_dict = {}
        children_dict = {}
        single_fields = []
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
            if mb_id not in mb_dict:
                mb = MetadataBlock(mb_id, DV_MB[mb_id])
                mb_dict[mb_id] = mb                        
            # has parent
            if parent != None:
                c_field = get_compound_field(parent, k, v, multiple)
                # MultipleCompoundField
                if isinstance(c_field, MultipleCompoundField):
                    children_dict[k] = []
                    if isinstance(v, list):
                        for value in v:          
                            p_field = get_p_field(type_class,k,[value],multiple,field)       
                            if p_field != None:            
                                children_dict[k].append(p_field) 
                    else:
                        p_field = get_p_field(type_class,k,v,multiple,field)                        
                        if p_field != None:            
                            children_dict[k].append(p_field)   
                # CompoundField
                if isinstance(c_field, CompoundField):
                    # PrimitiveFields                    
                    children_dict[k] = get_p_field(type_class,k,v,multiple,field)
                parents_dict[parent] = c_field
            # has no parent    
            if parent == None:
                p_field = get_p_field(type_class,k,v,multiple,field)
                if p_field != None and p_field.value != ['none'] and p_field.value != 'none':
                    mb_dict[mb_id].add_field(p_field) 
                    json_result.add_field(p_field)
        # build compound fields        
        for parent, c_field_outer in parents_dict.items():
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
                            print(child)
                            p_field = children_dict.get(child)[i]                      
                            if p_field != None and p_field.value != ['none'] and p_field.value != 'none' and p_field.value.strip() != '':
                                print(p_field.value)                            
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
                        if p_field != None and p_field.value != ['none'] and p_field.value != 'none' and p_field.value.strip() != '':
                            print(p_field.value)      
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
                dataset.add_block(mb_id,block)    
            create_dataset = CreateDataset(dataset)
            return create_dataset
        

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
        method = request.args.get('method',
                                  type=str,
                                  default='update')
        verbose = request.args.get('verbose',
                                  type=bool,
                                  default=False)        
        g.warnings=[]
        # get mapping for requested scheme        
        mapping = get_mapping(scheme,request.content_type)
        # read input depending on content-type and get all key-value-pairs in input
        reader = ReaderFactory.create_reader(request.content_type)        
        if reader is None:
            abort(415, scheme)        
        # translate key-value-pairs in input to target scheme
        source_key_values = reader.read(request.data, mapping)

        target_key_values = translate_source_keys(source_key_values, mapping)   

                #**************#
        # code for URL checking of Release Notes Field
        if "codeMetaReleaseNotes" in  target_key_values: #if codeMetaReleaseNotes field in dataverse's json then come inside this if 
            relnot_value = target_key_values["codeMetaReleaseNotes"] #take value of codeMetaReleaseNotes field
            relnot_value_s = ''.join(relnot_value) #convert from list to string 

            resp_url = check_value(relnot_value_s, "url") #check if value is valid or not?

            if resp_url == 0: #if url not valid then remove codeMetaReleaseNotes from output JSON and put warning 
                target_key_values.pop('codeMetaReleaseNotes')
                g.warnings.append("Wrong format of Release Notes, this field should be a URL. codeMetaReleaseNotes field removed")
                #print(g.warnings)
        #**************#

        #resp_url = check_value("Geeksoreeks1", "text")     testing text 
    
        # build json out of target_key_values and DV_FIELDS, DV_MB, DV_CHILDREN 
        result = build_json(target_key_values, method)  
        if method == 'edit':
            response = EditScheme().dump(result)
        elif method == 'update':
            response = DatasetSchema().dump(result)
        elif method == 'create':
            response = CreateDatasetSchema().dump(result) 
        if len(g.warnings) > 0:
            if verbose:
                response = verbosize(response)
            return jsonify(response), 202
        else:
            return jsonify(response), 200


    @app.route('/metadata/<string:scheme>')
    def getEmptyDataverseJson(scheme):
        """ Returns an empty JSON template for Dataverse with all mappable fields of the input metadata scheme. 
        
        Requires the mapping for scheme to exist.
        
        Parameters
        ----------
        scheme : str
        
        Returns
        ----------
        response : json              
        """
        method = request.args.get('method',
                                  type=str,
                                  default='update')
        verbose = request.args.get('verbose',
                                  type=bool,
                                  default=False)
        
        g.warnings = []        
        # get all target keys from scheme
        try:
            mapping = MAPPINGS.get(scheme)[0]
        except:
            abort(404, scheme)        
        target_keys = mapping.get_target_keys()                
        # build empty target key dictionary
        target_key_values = dict.fromkeys(target_keys, "")
        result = build_json(target_key_values, method)         
        if method == 'edit':
            response = EditScheme().dump(result)
        elif method == 'update':
            response = DatasetSchema().dump(result)
        elif method == 'create':
            response = CreateDatasetSchema().dump(result)              
        if len(g.warnings) > 0:
            if verbose == True:
                response = verbosize(response)
            return jsonify(response), 202
        else:
            return jsonify(response), 200


    @app.route('/mapping', methods=["GET"])
    def SchemasMappingInfo():
        """ Returns a general overview of existing mappings and formats. """
        list_of_mappings = []
        print((type(MAPPINGS['engmeta'][0])))
        for m in MAPPINGS:
            for mapping in MAPPINGS[m]:
                list_of_mappings.append(mapping.dump()) 
        return jsonify(list_of_mappings)


    @app.route('/mapping/<string:scheme>', methods=["GET"])
    def getSchemeMapping(scheme):
        """ Returns a mapping file for scheme. 
        If the scheme exists in several formats the query parameter has to be given. 
        """
        format = request.args.get('format', default=None)    
        mapping = get_mapping(scheme,format)
        return mapping.pretty_yaml()
    

    @app.route('/mapping', methods=["POST"])
    def createSchemaMapping():         
        """ Adds a new mapping. Aborts if target keys do not exist in DV_FIELDS. """
        new_mapping = request.data
        config = read_config(new_mapping)           
        # check if yaml file was correct    
        if len(g.warnings) > 0:
            warnings = ' '.join(g.warnings)
            abort(422,warnings)            
        fill_MAPPINGS(config)            
        with open("./resources/config/{}_{}.yml".format(config.scheme, config.format), "w") as f:        
            yaml.dump(yaml.safe_load(new_mapping), f)
        response = {'success': True,
                    'created': config.scheme,
                    'location': '/mapping/{}'.format(config.scheme)}        
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
        format = request.args.get('format', default=None)
        new_mapping = request.data
        try:
            mappings = MAPPINGS[scheme]          
        except:
            abort(404, scheme) # no existing mappings for scheme found
        if format == None:
            abort(400, scheme) # no format specified            
        config = read_config(new_mapping)         
        if config.format == format and config.scheme == scheme:
            if len(g.warnings) > 0:
                warnings = ' '.join(g.warnings)
                abort(422,warnings) # wrong values in yaml file
            else:
                for mapping in mappings:
                        if mapping.format == format: # success
                            mappings.remove(mapping)        
                            MAPPINGS[scheme] = mappings
                            fill_MAPPINGS(config)
                            with open("./resources/config/{}_{}.yml".format(config.scheme, config.format), "w") as f:        
                                yaml.dump(yaml.safe_load(new_mapping), f)
                            response = {'success': True,
                                        'updated': scheme}
                            return jsonify(response), 204
                        abort(400,scheme) # no mapping with the format found
        else:
            abort(400, scheme) # format/scheme in new yaml file does not correspond to the specified scheme/format
        
                
    
    @app.route('/mapping/<string:scheme>', methods=["DELETE"])
    def deleteSchemeMapping(scheme):
        """ Deletes a mapping for a metadata scheme. Fails if scheme or format not found. 
        
        Parameters
        ---------
        scheme : str
        
        Returns
        ---------
        response : json
        """
        format = request.args.get('format', default=None)   
        try:
            mappings = MAPPINGS[scheme]                 
        except:
            abort(404, scheme)
        if format == None and len(mappings) == 1:
            MAPPINGS[scheme] = []
            response = {'success': True,
                    'updated': scheme}
            return jsonify(response), 204
        for mapping in mappings:
            if mapping.format == format:
                mappings.remove(mapping)    
                os.remove("./resources/config/{}_{}.yml".format(scheme, format))    
                MAPPINGS[scheme] = mappings
                response = {'success': True,
                            'deleted': scheme}        
                return jsonify(response), 204        
        abort(400, scheme) 
        
        
    @app.route('/dv-metadata-config', methods=["GET"])
    def getMetadataBlocks():        
        """ Returns available metadata blocks. 
        
        Returns
        --------
        DV_MB : json
        """
        return jsonify(DV_MB)
        
    return app
