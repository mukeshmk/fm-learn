from flask import Blueprint, Flask, request, jsonify

from src.utils.constants import *

metrics_api = Blueprint('metrics_api', __name__)

from src.data_models.Metrics import *
from src.data_models.Params import *
from src.data_models.MetaFeatures import *

from app import db

# Create a Metric
@metrics_api.route('', methods=[POST])
def add_metric():
    algorithm_name = request.json['algorithm_name']
    dataset_hash = request.json['dataset_hash'].replace("\x00", "")
    metric_name = request.json['metric_name']
    metric_value = request.json['metric_value']

    target_type = request.json['target_type']

    new_metric = Metric(algorithm_name, dataset_hash, metric_name, metric_value, target_type)

    db.session.add(new_metric)
    db.session.commit()

    params = request.json['params']
    if(params != ""):
        for param in params:
            new_params = Params(new_metric.id, param['param_name'], param['param_value'])
            db.session.add(new_params)
    db.session.commit()

    data_meta_features = request.json['data_meta_features']
    if(data_meta_features != ""):
        for feat in data_meta_features:
            new_feat = MetaFeature(new_metric.id, feat['feat_name'], feat['feat_value'])
            db.session.add(new_feat)
    db.session.commit()

    return metric_schema.jsonify(new_metric)



# Get All Metrics
@metrics_api.route('', methods=[GET])
def get_metrics():
    all_metrics = Metric.query.all()
    result = metrics_schema.dump(all_metrics)
    if len(result) > 0:
        return jsonify(result)
    else:
        return jsonify('No Metric')


# Get Single Metric
@metrics_api.route(VAR_ID, methods=[GET])
def get_metric(id):
    metric = Metric.query.get(id)
    return metric_schema.jsonify(metric)


# Update a Metric
@metrics_api.route(VAR_ID, methods=[PUT])
def update_metric(id):
    metric = Metric.query.get(id)

    metric.algorithm_name = request.json['algorithm_name']
    metric.dataset_hash = request.json['dataset_hash'].replace("\x00", "")
    metric.metric_name = request.json['metric_name']
    metric.metric_value = request.json['metric_value']

    db.session.commit()

    return metric_schema.jsonify(metric)


# Delete Metric
@metrics_api.route(VAR_ID, methods=[DEL])
def delete_metric(id):
    metric = Metric.query.get(id)
    db.session.delete(metric)
    db.session.commit()

    return metric_schema.jsonify(metric)

# Retrieve all metric that matches the dataset_hash
@metrics_api.route(RETRIEVE + ALL, methods=[POST])
def retrieve_algorithm_list():
    dataset_hash = request.json['dataset_hash'].replace("\x00", "")

    all_metrics = Metric.query.filter_by(dataset_hash=dataset_hash).all()
    
    return metrics_schema.jsonify(all_metrics)


# Retrieve metric that best matches the dataset_hash
@metrics_api.route(RETRIEVE + MIN, methods=[POST])
def retrieve_algorithm_best_min():
    dataset_hash = request.json['dataset_hash'].replace("\x00", "")

    metric = Metric.query.filter_by(dataset_hash=dataset_hash).order_by(Metric.metric_value.asc()).first()

    return metric_schema.jsonify(metric)

# Retrieve metric that best matches the dataset_hash
@metrics_api.route(RETRIEVE + MAX, methods=[POST])
def retrieve_algorithm_best_max():
    dataset_hash = request.json['dataset_hash'].replace("\x00", "")

    metric = Metric.query.filter_by(dataset_hash=dataset_hash).order_by(Metric.metric_value.desc()).first()

    return metric_schema.jsonify(metric)
