# MetadataMapper

## How to run

Install dependencies: ```pip install requirements.txt```

Run server (in the folder v1): ```flask run```  or ```python __init__.py```

Run tests (in the folder test): ```python -m unittest ```

Build and run as docker container: 
```
docker build -t <image-name> .
docker run -e HOST_IP='0.0.0.0' -p 5000:5000/tcp <image-name> 
```
where ```<image-name>``` is a name of your choice, e.g. "metadata-mapper".

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

## GitHub Action

GitHub Action that can be used to first start the MetadataMapper and then make a post-request to it. This way one can convert metadata in the form of a codemeta-json-file into a Dataverse compatiple json-file. 

### Inputs

#### 'path'

**Required** path to the codemeta-json file in the repository. Default 'codemeta.json'.

### Outputs

#### 'post-result'

The result of the post-request to the MetadataMapper.

### Example Usage

```
on: [push]

jobs:
  api_request_job:
    runs-on: ubuntu-latest
    name: A job to make a post request to the MetadataMapper
    steps:
      # To use this repository's private action,
      # you must check out the repository
      - name: Checkout
        uses: actions/checkout@v3
      - name: MetadataMapper Action Step
        uses: ./ # Uses an action in the root directory
        id: api
        with:
          path: 'codemeta.json'
      # Use the output from the `MetadataMapper` step
      - name: Get the output
        run: |
          echo ${{ steps.api.outputs.post-result }}
```