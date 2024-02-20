# Metadata To Dataverse

Metadata2Dataverse is a small REST tool that aims to accomplish the following tasks:
- Conversion of structured metadata into a Dataverse-compliant JSON file
   - Input: Metadata in structured format
   - Output: Dataverse-compliant JSON file containing metadata based on the current metadata configuration (tsv files) of the Dataverse installation
- Register structured metadata formats and define mapping
- Test inconsistencies of mappings to current dataverse metadata configuration

## Usage
There are several options using this tool: Use it as [running service of your institution](#use-running-service), [deploy the tool yourself](#host-your-own-service), or use the provided [Github Action](#github-action).

### Use running service

You need to know the base URL where the tool is deployed to get started. Ask your local RDM team if and where they host the service. 
Then you can find a specification of all endpoints here.

#### Endpoints
see [OpenAPI documentation for more details](https://izus-fokus.github.io/metadata2dataverse/)

##### Metadata conversion

###### POST /metadata/<string:scheme>
Identification of the scheme in which the posted metadata file is stored.
- Query parameter method: Specifies the output format.
  - edit:compatible with the edit metadata endpoint,
  - update:compatible with the update metadata endpoint (default),
  - create:compatible to create a new record on Dataverse
- Query parameter verbose (boolean, default=False): Specifies whether additional information about the success should be given
- Body: Metadata file to be converted with Content-Type: text/plain, application/xml or application/json or application/jsonld
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

For development purposes or for testing run the server (in the folder v1) directly using flask: ```python __init__.py```
For production a different web server like [gunicorn](https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/) should be used.

##### Run tests
Rename the file ```credentials_default.json``` into ```credentials.json``` and insert base_url, api_key and the DOI of a test dataset. (See the [Dataverse Guides](https://guides.dataverse.org/en/latest/user/account.html#api-token) on how to create an API Token.)

Run tests (in the folder test): ```python -m unittest ```

##### Build and run as a docker container

```
docker build -t <image-name> .
docker run -e HOST_IP='0.0.0.0' -p 5000:5000/tcp <image-name> 
```
where ```<image-name>``` is a name of your choice, e.g. "metadata2dataverse".

### GitHub Action

This repository provides a GitHub Action that can be used to run the POST /metadata/<string:scheme> endpoint,
and then optionally update a dataset on Dataverse with the output metadata. 
In this way one can convert metadata in the form of a codemeta-json-file into a Dataverse compatiple json-file. 

Before using this action, the following steps have to be taken:
- First, you have to create a codemeta-file inside your repository. Have a look [here](https://codemeta.github.io/codemeta-generator/) for a generator.
- Second, if you want to update metadata of an existing Dataverse dataset, you need the PID (e.g., DOI) of this dataset. 
  Additionally, add your API-token from Dataverse as secret to your repository and call it DATAVERSE_API_TOKEN (or give it a different name, but remember to use the correct designation as input for api-key).

#### Inputs

|Parameter| Required? | Description | Default |
|-----|----|------|--------|
|path |**Required**| path to the codemeta-json file in the repository | Default 'codemeta.json' |
|dataverse-url |**Optional**| Server URL to Dataverse, e.g. 'https://darus.uni-stuttgart.de' | |
|doi|**Optional**| PID of the dataset in Dataverse, you want to update | |
|api-key|**Optional**| API-Token from Dataverse, you entered to the repository as secret. Enter it to the action in the form of: "api-key: '${{ secrets.DATAVERSE_API_TOKEN }}'". | |

#### Outputs

|Parameter | Description |
|metadata-mapper-result | The result of the POST-request to /metadata/codemeta?method=edit . |
|post-result| The result of the PUT-request to the editMetadata-endpoint of Dataverse with replace=True

#### Example Usage

```
on: [push]

jobs:
  api_request_job:
    runs-on: ubuntu-latest
    name: A job to make a post request to the MetadataMapper
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: MetadataMapper Action Step
        uses: izus-fokus/metadata2dataverse@v0.7
        id: api
        with:
          path: 'codemeta.json'
          dataverse-url: 'https://darus.uni-stuttgart.de'
          doi: '10.18419/darus-2935'
          api-key: '${{ secrets.DATAVERSE_API_TOKEN }}'
      # Use the output from the `MetadataMapper` step
      - name: Get the output
        run: |
          echo ${{ steps.api.outputs.metadata-mapper-result }}
          echo ${{ steps.api.outputs.post-result }}
```

### Configuration

After installing the dependencies but before running the service you might want to configure it.
There are two types of resources that you can replace to customize the tool for your individual dataverse installation:
* the dataverse metadata block definitions (.tsv files)
* the mapping configurations for the structure metadata formats you want to use as input (.yaml files)

Replace the tsv files in ```v1/resources/tsv/```. In this way the correct dataverse metadata definitions for your dataverse installation are already loaded when the service starts.
Analogous you can replace the yaml files in ```v1/resources/config```.

##### How to write mapping files
The heart of metadata2dataverse is the mapping of structured metadata input fields (```source_keys```) to dataverse metadata fields (```target_keys```).
The tool is flexible so that various mappings can be defined as long as the input file format is supported.

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
|reference (optional) | URL of further information or related publication to this scheme. |
|namespaces (optional)| List of xml namespaces in the form ```abbreviation=URI```. Example: ```[pm=http://www.loc.gov/premis/v3]``` |

Then, the keys ```mapping``` and ```rules``` define lists that express the translation of source keys to target keys. Most of the parameters of each item have defaults to facilitate compact definitions.

Each ```mapping``` list item can have the following keys:

|Key | Required? | Value | Default
|----|-------|-----------|---------|
|target_key | mandatory | string or list of strings, depending on ```type```. Dataverse metadata dataset field name as specified in a tsv file. | - |
|source_key | optional | string or list of strings, depending on ```type```. The values are written as keys in case format is 'text/plain', in [xpath syntax](https://lxml.de/) in case format is 'text/xml', and in [json path syntax](https://github.com/zhangxianbing/jsonpath-python) in case format is 'application/json'. | target_key |
|type | optional | One of 'copy', 'translate', 'merge', 'addition' | 'copy' if ```target_key``` is given, but not ```source_key```; 'translate' if both ```target_key``` and ```source_key``` are given. |
|priority | optional | integer specifying which definition should be preferred if more than one has the same ```target_key```; the value with the highest priority is taken | 1 |
|join_symbol | optional | if several ```source_keys``` shall be combined (```type``` 'merge'), the symbol between the values. | ' ' (space) |
|class | optional | class name inside the [AdditonTranslators module](/v1/models/AdditionTranslators.py), to generate values when a specific ```source key``` occurs (```type``` 'addition'). One of 'DateAdder', 'RoleNameAdder', 'IdentifierAdder'. | - |

Each ```rules``` list item can have the following keys:

|Key | Required? | Value | Default
|----|-------|-----------|---------|
|trigger | mandatory | ```source_key```; the values of this define the mapping. | - |
|priority | optional | integer specifying which definition should be preferred if more than one has the same ```trigger``` | 1 |
| \*; values of ```trigger``` | mandatory | list of mapping definitions (see table above) | - |

