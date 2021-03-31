# MetadataMapper

### How to run

### Requirements
```
pip install flask
pip install python-dotenv
pip install marshmellow
pip install marshmellow-oneofschema
```

Run server (in the folder v1): ```flask run```  or ```python __init__.py```

Run tests (in the folder test): ```python -m unittest ```

## Tasks
- Conversion of structured metadata into a Dataverse-compliant JSON file
  - Input: Metadata in structured format
  - Output: Dataverse-compliant JSON file containing metadata based on the current metadata configuration (tsv files) of the Dataverse installation

- Register structured metadata formats and define mapping
- Test inconsistencies of mappings to current dataverse metadata configuration

## Endpoints
### Metadatenconversion

#### POST /metadata/<string:scheme>
Identification of the scheme in which the posted metadata file is stored.
- Query parameter method: Specifies the output format. 
  - edit:compatible with the edit metadata endpoint, 
  - update:compatible with the update metadata endpoint (default), 
  - create:compatible to create a new record on Dataverse 
- Query parameter verbose (boolean, default=False): Specifies whether additional information about the success should be given
- Body: Metadata file to be converted with Content-Type: text/plain, application/xml or application/json
- Output: Dataverse-compatible JSON (verbose=false) or 
  ```
  {
   'success': <True|False>,
   'messages': [
      {'level': <error|warning|message>,
       'message': <textual message>
       },
    'result': <Dataverse-compatible JSON-Structure to be used for Edit, Update or Create-Endpoints>
   ]
  ```
