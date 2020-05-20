import pandas as pd
from utils import utils

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor

def kmc():
    df = utils.get_df_from_db()
    df.fillna(0, inplace=True)

    X, y = utils.get_Xy(df)

    # pre processing of data
    X, _ = utils.ohe_feature(X, utils.TARGET_TYPE)

    y, _ = utils.label_encode_feature(y, utils.ALGORITHM_NAME)
    y, _ = utils.label_encode_feature(y, utils.METRIC_NAME)

    # train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

    model = KNeighborsRegressor(n_neighbors=2)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print(y_test.to_string(header=False))
    y_pred = pd.DataFrame(y_pred)
    print(y_pred.to_string(header=False))

if __name__ == "__main__":
    kmc()
