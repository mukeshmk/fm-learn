import pandas as pd
from sklearn import preprocessing as pp

from src.data_models.Metrics import Metric

TARGET_TYPE = 'Target Type'
ALGORITHM_NAME = 'Algorithm Name'
METRIC_NAME = 'Metric Name'
METRIC_VALUE = 'Metric Value'
DATASET_HASH = 'Dataset Hash'
# INDEX - a column which gets added because each row in the SQL database creats a new dataframe
# which is created using `DataFrame.from_dict() which in turn is appended to a master df.
# TODO: try avoiding this!
INDEX = 'index'

def get_df_from_db():
    all_metrics = Metric.query.all()
    df = pd.DataFrame()
    for metric in all_metrics:
        data = {}
        if TARGET_TYPE not in data:
            data[TARGET_TYPE] = []
        data[TARGET_TYPE].append(str(metric.target_type))

        for mf in metric.meta_features:
            if mf.feat_name not in data:
                data[mf.feat_name] = []
            data[mf.feat_name].append(float(mf.feat_value))

        if ALGORITHM_NAME not in data:
            data[ALGORITHM_NAME] = []
        data[ALGORITHM_NAME].append(str(metric.algorithm_name))

        if METRIC_NAME not in data:
            data[METRIC_NAME] = []
        data[METRIC_NAME].append(str(metric.metric_name))

        if METRIC_VALUE not in data:
            data[METRIC_VALUE] = []
        data[METRIC_VALUE].append(float(metric.metric_value))

        if DATASET_HASH not in data:
            data[DATASET_HASH] = []
        data[DATASET_HASH].append(str(metric.dataset_hash))
        
        df = df.append(pd.DataFrame.from_dict(data))

    return df.reset_index()


def get_Xy(df):
    # the get_df_from_db() method gets (almost) all the rows from the SQL database
    # this list is used to remove columns which are not required for further processing
    # as the feature set (X) in the algorithm.
    # TODO: the function doesn't provide customisability with what X and y are being used.
    # may be add this in a future release and when updating the algorithm used to predict.
    unused_columns = [ALGORITHM_NAME, METRIC_NAME, METRIC_VALUE, DATASET_HASH, INDEX]

    X = df[df.columns.difference(unused_columns)]
    y = df[[DATASET_HASH]]
    return X, y

# One Hot Encoding
def ohe_feature(df, feature, drop_additional_feature=True):
    encoder = pp.OneHotEncoder(categories='auto', sparse=False)
    data = encoder.fit_transform(df[feature].values.reshape(len(df[feature]), 1))
    # creating the encoded df
    ohedf = pd.DataFrame(data, columns=[feature + ': ' + str(i.strip('x0123_')) for i in encoder.get_feature_names()])
    # to drop the extra column of redundant data
    if drop_additional_feature:
        ohedf.drop(ohedf.columns[len(ohedf.columns) - 1], axis=1, inplace=True)
    # concat the ohe df with the original df
    df = pd.concat([df, ohedf], axis=1)
    # to drop the original column in the df
    del df[feature]

    return df, encoder

# Label Encoding
def label_encode_feature(df, feature):
    encoder = pp.LabelEncoder()
    data = encoder.fit_transform(df[feature].values.reshape(len(df[feature]), 1))
    # to drop the original column in the df
    del df[feature]
    # creating the encoded df
    ledf = pd.DataFrame(data, columns=[feature])
    # concat the ohe df with the original df
    df = pd.concat([df, ledf], axis=1)

    return df, encoder
