import pandas as pd

from data_models.Metrics import Metric

from sklearn import preprocessing as pp

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

    df = pd.DataFrame.from_dict(data)
    return df


def get_Xy(df):
    X = df[df.columns.difference([ALGORITHM_NAME, METRIC_NAME, METRIC_VALUE])]
    y = df[[ALGORITHM_NAME, METRIC_NAME, METRIC_VALUE]]
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
