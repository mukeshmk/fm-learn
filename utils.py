import pandas as pd

from data_models.Metrics import Metric

TARGET_TYPE = 'Target Type'
ALGORITHM_NAME = 'Algorithm Name'
METRIC_NAME = 'Metric Name'
METRIC_VALUE = 'Metric Value'

def get_df_from_db():
    all_metrics = Metric.query.all()

    data = {}
    for metric in all_metrics:
        if TARGET_TYPE not in data:
            data[TARGET_TYPE] = []
        data[TARGET_TYPE].append(metric.target_type)

        for mf in metric.meta_features:
            if mf.feat_name not in data:
                data[mf.feat_name] = []
            data[mf.feat_name].append(mf.feat_value)
        
        if ALGORITHM_NAME not in data:
            data[ALGORITHM_NAME] = []
        data[ALGORITHM_NAME].append(metric.algorithm_name)
        
        if METRIC_NAME not in data:
            data[METRIC_NAME] = []
        data[METRIC_NAME].append(metric.metric_name)
        
        if METRIC_VALUE not in data:
            data[METRIC_VALUE] = []
        data[METRIC_VALUE].append(metric.metric_value)

    df = pd.DataFrame.from_dict(data)
    return df


def get_Xy(df):
    X = df[df.columns.difference([ALGORITHM_NAME, METRIC_NAME, METRIC_VALUE])]
    y = df[[ALGORITHM_NAME, METRIC_NAME, METRIC_VALUE]]
    return X, y
