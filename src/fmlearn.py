import time
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

from src.utils import utils

class fmlearn:

    def __init__(self):
        self._X = None
        self._y = None
        self._model = None

        # complete data frame used in fmlearn.
        self._df = None
        # stores the original shape of the dataframe before pre-processing
        self._shape = None
        # stores the time stamp of when the model was trained
        self._model_create_time = None
        self._accuracy = None

    def load_data(self):
        # loads data from the SQL database and pre-processes the data.
        self._df = utils.get_df_from_db()
        self._shape = self._df.shape

        # replacing NA values in the dataframe with -1
        self._df.fillna(-1, inplace=True)

        self._X, self._y = utils.get_Xy(self._df)

        # pre processing of data
        self._X, _ = utils.ohe_feature(self._X, utils.TARGET_TYPE)

        self._y, _ = utils.label_encode_feature(self._y, utils.DATASET_HASH)

    def train(self):
        if self._X is None:
            print('data not loaded! \nloading data and then training model')
            self.load_data()

        X_train, X_test, y_train, y_test = train_test_split(self._X, self._y, test_size=0.2, random_state=123)
        
        self._model = KNeighborsClassifier()
        self._model.fit(X_train, y_train)

        self._model_create_time = time.now()
        
        y_pred = self._model.predict(X_test)
        self._accuracy = accuracy_score(y_test, y_pred)

    def predict(self, X_pred):
        y_pred = self._model.predict(X_pred)
        return y_pred
        



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

    print(model.kneighbors(X_test)[1])
    print(y_test.to_string(header=False))
    y_pred = pd.DataFrame(y_pred)
    return y_pred.to_string(header=False)

if __name__ == "__main__":
    kmc()
