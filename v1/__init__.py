from api.app import create_app
from api import resources
from api.resources import read_all_config_files, read_all_tsv_files
from api.globals import MAPPINGS, DV_FIELD, DV_MB, DV_CHILDREN


app = create_app()
# read all files in resources/tsv and resources/config
read_all_config_files() # MAPPINGS
read_all_tsv_files()    # DV_FIELDS, DV_MB, DV_CHILDREN

print(MAPPINGS)
print(DV_FIELD)
print(DV_MB)
print(DV_CHILDREN)
if __name__ == '__main__':
    app.run()
