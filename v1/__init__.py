from api.app import create_app
from api import resources
from api.resources import read_all_config_files, read_all_scheme_files
from api.globals import MAPPINGS, DV_FIELD, DV_MB, DV_CHILDREN


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
