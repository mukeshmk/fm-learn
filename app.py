from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from src.config import *

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = LOCAL_SQLALCHEMY_DATABASE_URI
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = SERVER_SQLALCHEMY_DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

from src.api import metrics_api

app.register_blueprint(metrics_api, url_prefix='')

# added route for index.html webpage
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

# added route for api-description webpage
@app.route('/api-description.html')
def apidescription():
    return render_template('api-description.html')


# Run Server
if __name__ == '__main__':
    app.run()
