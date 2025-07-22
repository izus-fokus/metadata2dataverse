global MAPPINGS
global DV_FIELD 
global DV_MB 
global DV_CHILDREN
global SOURCE_KEYS

from pathlib import Path

# Base project directory (adjust based on your structure)
BASE_DIR = Path(__file__).parent.parent

# Path to credentials.json
CREDENTIALS_PATH = BASE_DIR / "cred/credentials.json"
# MAPPINGS - key: scheme (str), value: Config obj (list)
MAPPINGS = {}

# DV_FIELD - key: target key (str), value: Field obj
DV_FIELD = {}

# DV_MB - key: metadatablock name from scheme (str), value: display name from scheme (str)
DV_MB = {}

# DV_CHILDREN - key: parent (str), value: children (str)
DV_CHILDREN = {}

# SOURCE_KEY - 
SOURCE_KEYS = {}