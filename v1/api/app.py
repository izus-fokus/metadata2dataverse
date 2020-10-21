from flask import Flask, request, abort, jsonify, send_file
from api.globals import MAPPINGS, DV_FIELD, DV_MB, DV_CHILDREN
from models.ReaderFactory import ReaderFactory
from models.MetadataModel import EditFormat, EditScheme, PrimitiveField, CompoundField, MultipleCompoundField, MultiplePrimitiveField, PrimitiveFieldScheme, CompoundFieldScheme, MultipleCompoundFieldScheme, MultiplePrimitiveFieldScheme
from api.resources import read_all_config_files, read_all_tsv_files
from asn1crypto.core import Primitive
from pkg_resources._vendor.pyparsing import empty

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
        
    # helper functions

    def verbose(response, warnings=[]):
        return {'success': True,
                'warnings': warnings,
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
        for k, v in source_key_values.items():
            t = mapping.get_translator(k)
            target_key = t.target_key
            target_key_values[target_key] = v
        return target_key_values
    
    def get_format(method):
        if method == 'update':
            return EditFormat()
        # elif method == 'update':
        #    return ?
    
    def build_json(target_key_values, method):
        json_result = get_format(method)
        parents_dict = {}
        primitives_dict = {}
        for k, v in target_key_values.items():
            field = DV_FIELD.get(k)
            parent = field.parent
            type_class = field.type_class
            multiple = field.multiple
            
            # PrimitiveFields
            if type_class == "primitive" or "controlled_vocabulary":
                if multiple == True:
                    p_field = MultiplePrimitiveField(k,v)
                if multiple == False:
                    if isinstance(v, list):
                        concatenated = ""
                        for value in v:
                            concatenated += value + ", "
                        p_field = PrimitiveField(k,concatenated[:-2])                        
                    else:    
                        p_field = PrimitiveField(k,v)      
            # has parent
            if parent != None:
                parent_field = DV_FIELD.get(parent)
                parent_field_multiple = parent_field.multiple
                # MultipleCompoundField
                if parent_field_multiple == True:
                    c_field = MultipleCompoundField(parent)
                    primitives_dict[k] = []
                    if isinstance(v, list):
                        for value in v:          
                            primitives_dict[k].append(PrimitiveField(k,value)) 
                    else:
                        primitives_dict[k].append(PrimitiveField(k,v))        
                # CompoundField
                if parent_field_multiple == False:
                    c_field = CompoundField(parent)    
                    primitives_dict[k] = p_field
                parents_dict[parent] = c_field           
            # has no parent
            if parent == None: 
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
                           c_field_inner.add_value(p_field, child)
                    c_field_outer.add_value(c_field_inner)
                    
                json_result.add_field(c_field_outer)
            else:
                for child in children:
                    if child in primitives_dict:  
                        p_field = primitives_dict.get(child)
                        c_field_outer.add_value(p_field, child)
                json_result.add_field(c_field_outer) 
        
        return json_result
        
    @app.route('/metadata/<string:scheme>', methods=["POST"])
    def mapMetadata(scheme):
        method = request.args.get('method',
                                  type=str,
                                  default='update')
        warnings = []
        
        # get mapping for requested scheme        
        mapping = get_mapping(scheme)
        
        # get all source keys of scheme
        list_of_source_keys = mapping.get_source_keys()
        
        # read input depending on content-type and get all key-value-pairs in input
        reader = ReaderFactory.create_reader(request.content_type)        
        source_key_values = reader.read(request.data, list_of_source_keys) 
        
        # translate key-value-pairs in input to target scheme
        target_key_values = translate_source_keys(source_key_values, mapping)
        
        # build json out of target_key_values and DV_FIELDS, DV_MB, DV_CHILDREN       
        result = build_json(target_key_values, method)      

        if method == 'update':
            response = EditScheme().dump(result)
                       

        if len(warnings) > 0:
            if verbose:
                verbosize(response)
            return jsonify(response), 202

        else:
            return jsonify(response), 200


    @app.route('/metadata/<string:scheme>')
    def getEmptyDataverseJson(scheme):
        method = request.args.get('method',
                                  type=str,
                                  default='update')
        warnings = []
        # get all target keys from mapping
        # mapping = Mapping.query.get(scheme)
        #if mapping is None:
        #    abort(404,
        #          '''Scheme {} not found. 
        #             Get available schemes 
        #             with GET /metadata'''
        #          .format(scheme))
        # target_keys = mapping.target_keys
        # response = getModel(method,target_keys)
        response = {}
        # build JSON-Structure from tsv-information

        if len(warnings) > 0:
            if verbose:
                verbose(response)
            return jsonify(response), 202

        else:
            return jsonify(response), 200


    @app.route('/mapping', methods=["GET"])
    def SchemasMappingInfo():
        # get all available mappings
        # mappings = Mapping.query.all()
        mappings = []
        if(len(mappings) == 0):
            abort(404, 'No mappings available')

        return jsonify({'success': True,
                        'schemes': [m.dump() for m in mappings]})

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
