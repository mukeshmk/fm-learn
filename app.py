import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


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
    dataset_hash = request.json['dataset_hash']
    metric_name = request.json['metric_name']
    metric_value = request.json['metric_value']
    
    new_metric = Metric(algorithm_name, dataset_hash, metric_name, metric_value)

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

# Retrieve all metric that matches the dataset_hash
@app.route('/metric/retrieve/all', methods=['POST'])
def retrieve_algorithm_list():
    dataset_hash = request.json['dataset_hash']
    all_metrics = Metric.query.filter_by(dataset_hash=dataset_hash).all()
    result = metrics_schema.dump(all_metrics)
    return jsonify(result)


# Retrieve metric that best matches the dataset_hash
@app.route('/metric/retrieve/best', methods=['POST'])
def retrieve_algorithm_best():
    dataset_hash = request.json['dataset_hash']

    metric = db.Table('metrics', db.metadata, autoload=True, autoload_with=db.engine)

    all_metrics = db.engine.connect().execute(
        db.select([metric])
        .order_by(db.asc(metric.columns.metric_value))
        .where(metric.columns.dataset_hash.in_([dataset_hash]))
    ).first()
    return metric_schema.jsonify(all_metrics)

# Run Server
if __name__ == '__main__':
    app.run()
