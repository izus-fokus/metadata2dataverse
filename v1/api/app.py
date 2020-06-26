from flask import Flask, request, abort, jsonify, send_file
from api.globals import MAPPINGS, DV_FIELD, DV_MB, DV_CHILDREN


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

    @app.route('/metadata/<string:scheme>', methods=["POST"])
    def mapMetadata(scheme):
        method = request.args.get('method',
                                  type=str,
                                  default='update')
        warnings = []

        # mapping = MAPPINGS.get(scheme)
        # if mapping is None:
        #    abort(404,
        #          '''Scheme {} not found. 
        #             Check GET /mapping for available schemes.'''
        #          .format(scheme))
        # check input file for the right format
        # if request.headers.get('Content-Type') !== mapping.format:
        #   abort (415, '''The request media type is not supported for 
        #               '{}'. Check resource `/mapping/engMeta` 
        #               for available media types of this metadata scheme'''.format(scheme))                         
        # parse input file
        # translators = mapping.translators
        # response = mapping.getModel(method,target_keys)
        response = {}
        # build JSON-Structure from tsv-information

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
        
        print(MAPPINGS)
    
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
        
        #return jsonify(response), 201, {'Location': '/mapping/{}'.format(m.name)}


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
