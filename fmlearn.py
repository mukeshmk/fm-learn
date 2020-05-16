import pandas as pd
import utils

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor

def kmc():
    df = utils.get_df_from_db()

    df, _ = utils.ohe_feature(df, utils.TARGET_TYPE)
    X, y = utils.get_Xy(df)

    y, _ = utils.ohe_feature(y, utils.ALGORITHM_NAME, False)
    y, _ = utils.ohe_feature(y, utils.METRIC_NAME, False)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

    model = KNeighborsRegressor(n_neighbors=2)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(y_pred)
    print(y)
    print(y_test)


if __name__ == "__main__":
    kmc()