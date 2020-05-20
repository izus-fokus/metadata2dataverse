from api.app import create_app

MAPPINGS = {} # dict of Config-Objects 

DV_CONFIG = {} # dict of MetadataBlock-Objects

app = create_app()

# read all files in resources/tsv in DV_CONFIG
# read all files in resources/config in MAPPINGS

if __name__ == '__main__':
    app.run()
