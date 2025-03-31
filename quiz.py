from flask import Flask
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)


import controllers.config as config 
import models.models as models
import controllers.routes as routes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5501, debug=True)