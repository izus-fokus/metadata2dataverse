from api.app import create_app
from api import resources
from api.resources import read_all_config_files, read_all_tsv_files

MAPPINGS = {} # dict of Config-Objects 

DV_FIELDS = {} # dict of MetadataBlock-Objects
DV_MB = {} # dict of MetadataBlock Fieldnames
DV_CHILDREN = {} # dict of parent target keys and their children

app = create_app()

# read all files in resources/tsv in DV_CONFIG
#read_all_config_files()
read_all_tsv_files()

# read all files in resources/config in MAPPINGS

if __name__ == '__main__':
    app.run()
