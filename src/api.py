from flask import Blueprint, Flask, request, jsonify
import pandas as pd

from src.utils.constants import *

metrics_api = Blueprint('metrics_api', __name__)

from src.data_models.Metrics import *
from src.data_models.Params import *
from src.data_models.MetaFeatures import *

from app import db

from src.fmlearn import fmlearn
from src.utils import utils

# global FMLearn object which is to be used across the application
# for algorithm predection (at least that's the plan)
fml = fmlearn()

# doing this so that dataload and training of the model happens once at application start.
fml.load_data()
fml.train()

# Create a Metric
@metrics_api.route('', methods=[POST])
def add_metric():
    algorithm_name = request.json[ALGORITHM_NAME]
    dataset_hash = request.json[DATASET_HASH].replace("\x00", "")
    metric_name = request.json[METRIC_NAME]
    metric_value = request.json[METRIC_VALUE]

    target_type = request.json[TARGET_TYPE]

    new_metric = Metric(algorithm_name, dataset_hash, metric_name, metric_value, target_type)

    db.session.add(new_metric)
    db.session.commit()

    params = request.json[PARAMS]
    if(params != ""):
        for param in params:
            new_params = Params(new_metric.id, param[PARAM_NAME], param[PARAM_VALUE])
            db.session.add(new_params)
        db.session.commit()

    data_meta_features = request.json[META_FEATURES]
    if(data_meta_features != ""):
        for feat in data_meta_features:
            new_feat = MetaFeature(new_metric.id, feat[FEAT_NAME], feat[FEAT_VALUE])
            db.session.add(new_feat)
        db.session.commit()

    return metric_schema.jsonify(new_metric)


# Retrieve all metric that matches the dataset_hash
@metrics_api.route(RETRIEVE + ALL, methods=[POST])
def retrieve_algorithm_list():
    dataset_hash = request.json[DATASET_HASH].replace("\x00", "")

    all_metrics = Metric.query.filter_by(dataset_hash=dataset_hash).all()
    
    return metrics_schema.jsonify(all_metrics)


# Retrieve metric that best matches the dataset_hash
@metrics_api.route(RETRIEVE + MIN, methods=[POST])
def retrieve_algorithm_best_min():
    dataset_hash = request.json[DATASET_HASH].replace("\x00", "")

    metric = Metric.query.filter_by(dataset_hash=dataset_hash).order_by(Metric.metric_value.asc()).first()

    return metric_schema.jsonify(metric)


# Retrieve metric that best matches the dataset_hash
@metrics_api.route(RETRIEVE + MAX, methods=[POST])
def retrieve_algorithm_best_max():
    dataset_hash = request.json[DATASET_HASH].replace("\x00", "")

    metric = Metric.query.filter_by(dataset_hash=dataset_hash).order_by(Metric.metric_value.desc()).first()

    return metric_schema.jsonify(metric)


########### API CURRENTLY NOT IN USE BY SCIKIT-LEARN ###########


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

    metric.algorithm_name = request.json[ALGORITHM_NAME]
    metric.dataset_hash = request.json[DATASET_HASH].replace("\x00", "")
    metric.metric_name = request.json[METRIC_NAME]
    metric.metric_value = request.json[METRIC_VALUE]

    db.session.commit()

    return metric_schema.jsonify(metric)


# Delete Metric
@metrics_api.route(VAR_ID, methods=[DEL])
def delete_metric(id):
    metric = Metric.query.get(id)
    db.session.delete(metric)
    db.session.commit()

    return metric_schema.jsonify(metric)


# test API for fmlearn
# TODO: imporove performance? seems way too overcomplicated
@metrics_api.route('test', methods=[GET])
def test_fmlearn():
    dataset_hash = request.json[DATASET_HASH].replace("\x00", "")
    target_type = request.json[TARGET_TYPE]
    data_meta_features = request.json[META_FEATURES]

    data = {}
    
    # fetching the encoder for target type for encoding the input data
    tt_encoder = fml.get_encoders()[utils.TARGET_TYPE]
    # fetching the columns used in the dataframe for the said encoder
    tt_cols = [utils.TARGET_TYPE + ': ' + str(i.strip('x0123_')) for i in tt_encoder.get_feature_names()]

    # creating a dataframe of target type to endode
    tt = pd.DataFrame([str(target_type)])
    
    # creating a dataframe after encoding with the appropriate columns names
    tt = pd.DataFrame(tt_encoder.transform(tt), columns = tt_cols)
    # removing the last columns in the case of OHE
    tt = tt.iloc[:, :-1]

    # creating a dataframe with all cols the X df
    df = pd.DataFrame(columns = fml.get_X_cols())

    # converting the json into a dataframe which can be used as input to predict()
    if(data_meta_features != ""):
        for feat in data_meta_features:
            if feat[FEAT_NAME] not in data:
                data[feat[FEAT_NAME]] = []
            data[feat[FEAT_NAME]].append(float(feat[FEAT_VALUE]))

    df = df.append(pd.DataFrame.from_dict(data))

    # merging target type encoded columns with the final df
    for i in range(len(tt_cols) - 1):
            df[tt_cols[i]] = tt[tt_cols[i]]

    # replacing NA values in the dataframe with -1
    # NA values are possible because the shape of df is difference for regression and classification probs
    # and since `fml.get_X_cols()` ensures that all columns are used for the df there is a possibility of NA values
    df.fillna(-1, inplace=True)

    return str(fml.predict(df))
