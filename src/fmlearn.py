import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from src.utils import utils

def kmc():
    df = utils.get_df_from_db()
    df.fillna(-1, inplace=True)

    X, y = utils.get_Xy(df)

    # pre processing of data
    X, _ = utils.ohe_feature(X, utils.TARGET_TYPE)

    y, _ = utils.label_encode_feature(y, utils.DATASET_HASH)

    # train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

    model = KNeighborsClassifier()

    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)

    print(y_test.to_string(header=False))
    y_pred = pd.DataFrame(y_pred)
    return y_pred.to_string(header=False)

if __name__ == "__main__":
    kmc()
