from flask import Flask, request, abort, jsonify, send_file, g
from api.globals import MAPPINGS, DV_FIELD, DV_MB, DV_CHILDREN
from api.resources import read_all_config_files, read_all_tsv_files
from models.ReaderFactory import ReaderFactory
from models.Translator import MergeTranslator, AdditionTranslator
from models.MetadataModel import MultipleVocabularyField, VocabularyField, CreateDatasetSchema, CreateDataset, DatasetSchema, MetadataBlock, MetadataBlockSchema, Dataset, EditFormat, EditScheme, PrimitiveField, CompoundField, MultipleCompoundField, MultiplePrimitiveField, PrimitiveFieldScheme, CompoundFieldScheme, MultipleCompoundFieldScheme, MultiplePrimitiveFieldScheme
from builtins import isinstance
# from api.resources import read_all_config_files, read_all_tsv_files
# from asn1crypto.core import Primitive
# from pkg_resources._vendor.pyparsing import empty

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
        
    # helper functions
    @app.before_first_request
    def init_globals():
        read_all_config_files()
        read_all_tsv_files()

    def verbosize(response):
        return {'success': True,
                'warnings': g.warnings,
                'response': response
                }

    def gen_message(warnings):
        return '. '.join(warnings)

    def get_mapping(scheme):
        mapping = MAPPINGS.get(scheme)
        if mapping is None:
            abort(404, '''Scheme {} not found. Check GET /mapping for available schemes.'''.format(scheme))
        return mapping
    
    def translate_source_keys(source_key_values, mapping):
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
        # Primitive
        if type_class == "primitive":
            p_field = get_primitive_field(k,v,multiple)
        # Controlled Vocabulary
        if type_class == "controlled_vocabulary":
            if v == "":        # special case for getEmptyDataverseJson
                p_field = get_vocabulary_field(k, v, multiple)
            v_checked = field.check_controlled_vocabulary(v)
            if len(v_checked) > 0:
                p_field = get_vocabulary_field(k, v_checked, multiple)                
            else: 
                g.warnings.append("Use controlled vocabulary for " + k + ": " + str(field.controlled_vocabulary))
        return p_field
    
    def get_primitive_field(k,v,multiple):        
        if multiple == True:
            if isinstance(v,list):
                v_new = []
                for value in v:
                    if value != 'none' and value != None:
                        v_new.append(value)
                v = v_new
            p_field = MultiplePrimitiveField(k,v)
        if multiple == False:            
            if isinstance(v, list):
                v_new = ""
                counter = 0
                for value in v:
                    if value != 'none' and value != None:
                        counter += 1
                        if counter == 1:
                            v_new += value
                        else:
                            g.warnings.append(k + " has only one allowed value. We deleted value number " + str(counter) + ": " + value)
                v = v_new
            p_field = PrimitiveField(k,v)
        return p_field
    
    def get_vocabulary_field(k, v, multiple):
        if multiple == True:
            if not isinstance(v,list):
                v = [v]
            v_field = MultipleVocabularyField(k,v)
        if multiple == False:
            if isinstance(v,list):
                v = ", ".join(v)
            v_field = VocabularyField(k,v)   
        return v_field
    
    def build_json(target_key_values, method):
        json_result = EditFormat() 
        parents_dict = {}
        primitives_dict = {}
        single_fields = []
        mb_dict = {}
        for k, v in target_key_values.items():    
            field = DV_FIELD.get(k)
            if field is None:
                g.warnings.append("Field {} not in Dataverse-Konfiguration".format(k))
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
                    primitives_dict[k] = []
                    if isinstance(v, list):
                        for value in v:          
                            primitives_dict[k].append(PrimitiveField(k,value)) 
                    else:
                        primitives_dict[k].append(PrimitiveField(k,v))        
                # CompoundField
                if isinstance(c_field, CompoundField):
                    # PrimitiveFields                    
                    primitives_dict[k] = get_p_field(type_class,k,v,multiple,field)
                parents_dict[parent] = c_field
            # has no parent    
            if parent == None:
                p_field = get_p_field(type_class,k,v,multiple,field)
                mb_dict[mb_id].add_field(p_field) 
                json_result.add_field(p_field)
                
        # build compound fields        
        for parent, c_field_outer in parents_dict.items(): 
            children = DV_CHILDREN.get(parent)             
            if isinstance(c_field_outer, MultipleCompoundField):            
                for child in children:                    
                    if child in primitives_dict:
                        number_of_values = len(primitives_dict.get(child))
                        break                                   
                for i in range(number_of_values):    
                    c_field_inner = CompoundField(parent)                
                    for child in children:                                                
                        if child in primitives_dict: 
                           p_field = primitives_dict.get(child)[i]                           
                           if p_field.value != 'none':                           
                               c_field_inner.add_value(p_field, child)                               
                           else:
                                continue
                    if bool(c_field_inner.value):
                        c_field_outer.add_value(c_field_inner)
                json_result.add_field(c_field_outer)
                mb_dict[mb_id].add_field(c_field_outer)
            else:
                for child in children:
                    if child in primitives_dict:  
                        p_field = primitives_dict.get(child)
                        c_field_outer.add_value(p_field, child)
                json_result.add_field(c_field_outer)     
                mb_dict[mb_id].add_field(c_field_outer)
        
        if method == 'update':            
            dataset = Dataset()
            for mb, block in mb_dict.items():
                dataset.add_block(block)                
            return dataset
            
        if method == 'edit':
            return json_result
        
        if method == 'create':
            dataset = Dataset()
            for mb, block in mb_dict.items():
                dataset.add_block(block)    
            create_dataset = CreateDataset(dataset)
            return create_dataset
               
            
    def get_compound_field(parent,k,v,multiple):
        parent_field = DV_FIELD.get(parent)
        parent_field_multiple = parent_field.multiple
        if parent_field_multiple == True:
            c_field = MultipleCompoundField(parent)
        if parent_field_multiple == False:
            c_field = CompoundField(parent)    
        return c_field
    
 
    @app.route('/metadata/<string:scheme>', methods=["POST"])
    def mapMetadata(scheme):
        method = request.args.get('method',
                                  type=str,
                                  default='update')
        verbose = request.args.get('verbose',
                                  type=bool,
                                  default=False)
        
        g.warnings=[]
        
        # get mapping for requested scheme        
        mapping = get_mapping(scheme)
        
        # read input depending on content-type and get all key-value-pairs in input
        reader = ReaderFactory.create_reader(request.content_type)        
        if reader is None:
            abort(404, '''Content-Type {} not found. Check GET /mapping for available schemes.'''.format(request.content_type))
        
        # translate key-value-pairs in input to target scheme
        source_key_values = reader.read(request.data, mapping) 
        target_key_values = translate_source_keys(source_key_values, mapping)
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
            return response, 202

        else:
            return jsonify(response), 200


    @app.route('/metadata/<string:scheme>')
    def getEmptyDataverseJson(scheme):
        method = request.args.get('method',
                                  type=str,
                                  default='update')
        g.warnings = []
        # get all target keys from scheme
        mapping = get_mapping(scheme)
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
            if verbose:
                verbosize(response,g.warnings)
            return jsonify(response), 202

        else:
            return jsonify(response), 200


    @app.route('/mapping', methods=["GET"])
    def SchemasMappingInfo():
        # get all available mappings
        # mappings = Mapping.query.all()
        if(len(MAPPINGS) == 0):
            abort(404, 'No mappings available')
        return jsonify({'success': True,
                        'schemes': [MAPPINGS[m].dump() for m in MAPPINGS]})

    @app.route('/mapping', methods=["POST"])
    def createSchemaMapping():         
    
        # read input stream and parse information in JSON Object
        # 
        # check for required fields
        # add mapping to DB
        # check, if mapping already exists
        # mapping = Mapping.query.filter(Mapping.name == m.name).first()
        # mapping = None
        # if mapping is not None:
        #    abort(409, 'A mapping with the name "{}" already exists. Use PUT /mapping/{} to change it.'.format(m.name))        
        #else:
        #    errors = []
        # mapping = Mapping(name='',description='',format='',reference='')
        # go through mapping and add translators
        # for m in mapping:
        # mapping.add_translator(type=m.type, m)
        # errors beim Parsen der Translators füllen

        # existenz aller target_keys in metadaten-konfiguration prüfen
        # sonst in in Errors schreiben
        # hier factory erzeugen?
        #    if len(errors) > 0:
        #        abort(422, 'Unprocessable entity - validation failed. {}'.format(gen_message(errors)))
        #response = {'success': True,
        #            'created': m.name}
        
        return jsonify(response), 201, {'Location': '/mapping/{}'.format(m.name)}


    @app.route('/mapping/<string:scheme>', methods=["GET"])
    def getSchemeMapping(scheme):
        format = request.args.get('format', default=None)
        # mapping = get_mappings(scheme, format)
        # if len(mappings) > 0:
        # abort(400, "Scheme'{}' exists in different formats. Check resource `/mapping` for available schemes/formats and specify format in your request.".format(scheme)) 
        if mapping is None:
            abort(404, "Did not find mapping schema '{}'. Check resource `/mapping` for available schemes".format(scheme))

        # get file
        file = mapping.file
        try:
            send_file(file)
        except:
            abort(422)

    @app.route('/mapping/<string:scheme>', methods=["PUT"])
    def editSchemeMapping(scheme):
        format = request.args.get('format', default=None)
        # check, if mapping exists, otherwise abort(404)
        # check, if mapping has more than one format and a format is specified, otherwise abort(400)
        # parse input-file and validate, otherwise abort(422)
        # update mapping
        # replace file in resources 
        response = {'success': True,
                    'updated': scheme}
        return jsonify(response), 204
    
    @app.route('/mapping/<string:scheme>', methods=["DELETE"])
    def deleteSchemeMapping(scheme):
        format = request.args.get('format', default=None)
        #check, if scheme is available, otherwise abort(404)
        # check, if scheme is identified with format, otherwise abort (400)


        response = {'success': True,
                    'deleted': scheme,
                    'format': format}
        return jsonify(response)

    return app
