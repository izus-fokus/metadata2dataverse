import os
from api.app import create_app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host=os.environ.get('HOST_IP','127.0.0.1'))
