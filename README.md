# Metadata To Dataverse

Metadata2Dataverse is a small REST tool that aims to accomplish the following tasks:
- Conversion of structured metadata into a Dataverse-compliant JSON file
   - Input: Metadata in structured format
   - Output: Dataverse-compliant JSON file containing metadata based on the current metadata configuration (tsv files) of the Dataverse installation
- Register structured metadata formats and define mapping
- Test inconsistencies of mappings to current dataverse metadata configuration

## Usage
There are two main options using this tool: Use it as running service of your institution or deploy the tool yourself.

### Use running service

You need to know the base URL where the tool is deployed to get started. Ask your local RDM team if and where they host the service. 
Then you can find a specification of all endpoints here.

#### Endpoints
##### Metadata conversion

###### POST /metadata/<string:scheme>
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


### Host your own service

#### Deploy

Install dependencies: ```pip install -r requirements.txt```

For development purposes or for testing run the server (in the folder v1) directly using flask: ```flask run```  or ```python __init__.py```
For production a different web server like [gunicorn](https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/) should be used.

Run tests (in the folder test): ```python -m unittest ```

Build and run as docker container: 
```
docker build -t <image-name> .
docker run -e HOST_IP='0.0.0.0' -p 5000:5000/tcp <image-name> 
```
where ```<image-name>``` is a name of your choice, e.g. "metadata2dataverse".

#### Configuration

After installing the dependencies but before running the service you might want to configure it.
There are two types of resources that you can replace to customize the tool for your individual dataverse installation:
* the dataverse metadata block definitions (.tsv files)
* the mapping configurations for the structure metadata formats you want to use as input (.yaml files)

Replace the tsv files in ```v1/resources/tsv/```. In this way the correct dataverse metadata definitions for your dataverse installation are already loaded when the service starts.
Analogous you can replace the yaml files in ```v1/resources/config```.

##### How to write mapping files
The heart of metadata2dataverse is the mapping of structured metadata input fields (```source_keys```) to dataverse metadata fields (```target_keys```).
The tool is flexible so that arbitrary mappings can be defined as long as the input file format is supported.

At the moment the following formats are supported:
* xml
* json
* [ExtractIng](https://github.com/bjschembera/ExtractIng) txt format

Each mapping file starts with some header keys providing general information:

|Key | Value |
|----|-------|
|scheme| Name of the structured metadata this mapping configuration is for. Is used as path parameter in REST calls, so used symbols should be URL compatible. Example: 'codemeta' |
|description| Human readable description of the scheme, containing, e.g., informations about scheme versions this mapping file is for. |
|format| MIME type of the structured metadata. One of: ```text/xml```, ```application/json```, ```text/plain```. |
|namespaces (optional)| List of xml namespaces in the form ```abbreviation=URI```. Example: ```[pm=http://www.loc.gov/premis/v3]``` |

Then, below the key ```mapping```, the rules for mapping source keys to target keys are defined in a list. Most of the parameters of each rule have defaults to facilitate compact definitions.
Each mapping rule can have the following keys:

|Key | Required? | Value | Default
|----|-------|-----------|---------|
|source_key | mandatory | string or list of strings, depending on ```type```. The values are written as keys in case format is text/plain, in xpath syntax in case format is text/xml, and in json path syntax in case format is application/json. | - |
|target_key | optional | The dataverse metadata dataset field name as specified in a tsv file. | source_key |
|type | optional | One of copy, merge, addition or rule | copy
