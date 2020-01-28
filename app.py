import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from cryptography.fernet import Fernet
from encryption.key import FMLKey


app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/testdb01'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

from Metrics import *

# Create a Metric
@app.route('/metric', methods=['POST'])
def add_metric():
    algorithm_name = request.json['algorithm_name']
    encrypted_dataset_hash = request.json['dataset_hash']
    metric_name = request.json['metric_name']
    metric_value = request.json['metric_value']
    
    new_metric = Metric(algorithm_name, encrypted_dataset_hash, metric_name, metric_value)

    db.session.add(new_metric)
    db.session.commit()

    return metric_schema.jsonify(new_metric)



# Get All Metrics
@app.route('/metric', methods=['GET'])
def get_metrics():
    all_metrics = Metric.query.all()
    result = metrics_schema.dump(all_metrics)
    if len(result) > 0:
        return jsonify(result)
    else:
        return jsonify('No Metric')


# Get Single Metric
@app.route('/metric/<id>', methods=['GET'])
def get_metric(id):
    metric = Metric.query.get(id)
    return metric_schema.jsonify(metric)


# Get Single Decrypted Metric
@app.route('/metric/<id>/decrypt', methods=['GET'])
def get_decrypted_metric(id):
    metric = Metric.query.get(id)
    
    key = FMLKey()
    f = Fernet(key.getKey())
    dataset_unhashed = f.decrypt(bytes(metric.dataset_hash, encoding='UTF-8')).decode('utf-8')

    new_metric = Metric(metric.algorithm_name, dataset_unhashed, metric.metric_name, metric.metric_value)
    new_metric.id = metric.id
    return metric_schema.jsonify(new_metric)


# Update a Metric
@app.route('/metric/<id>', methods=['PUT'])
def update_metric(id):
    metric = Metric.query.get(id)

    algorithm_name = request.json['algorithm_name']
    dataset_hash = request.json['dataset_hash']
    metric_name = request.json['metric_name']
    metric_value = request.json['metric_value']

    metric.algorithm_name = algorithm_name
    metric.dataset_hash = dataset_hash
    metric.metric_name = metric_name
    metric.metric_value = metric_value

    db.session.commit()

    return metric_schema.jsonify(metric)


# Delete Metric
@app.route('/metric/<id>', methods=['DELETE'])
def delete_metric(id):
    metric = Metric.query.get(id)
    db.session.delete(metric)
    db.session.commit()

    return metric_schema.jsonify(metric)


# Run Server
if __name__ == '__main__':
    app.run()
