import json
import sys
from pathlib import Path

import pytest

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

def pytest_addoption(parser):
    parser.addoption('--apikey', action='store', default='<add Dataverse API-Key>', help='add Dataverse API-Key')
    parser.addoption('--apiurl', action='store', default='http://localhost:8080', help='add Dataverse API-URL')


@pytest.fixture(scope='session')
def credentials():
    with open("../cred/credentials.json", "r") as cred_file:
        credentials = json.load(cred_file)
        credentials["api_key"] = sys.argv[1][len("--apikey="):]
        credentials["base_url"] = sys.argv[2][len("--apiurl="):]
        return credentials