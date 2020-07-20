import math
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

from src.utils import utils

class fmlearn:

    MAX_NEW_RECORDS = 10

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
        # to store feature encoders
        self._encoders = {}
        # boolean to track retraining of the model
        self._retain = False
        # counter to keep track of no of new records which were added to dataset
        # after the last model was trained.
        self._new_recs = 0

    def get_encoders(self):
        return self._encoders

    def get_X_cols(self):
        return self._X.columns

    def new_record_added(self):
        if self._new_recs == math.inf:
            self._new_recs = 1
        self._new_recs += 1
        return

    def is_model_trained(self):
        return self._model is not None

    def load_data(self):
        # force new model to be trained once data has been reloaded
        # retraining of model occurs only when the predict() function is being called
        # this is due to absense of background processes framework in the application.
        self._retain = True

        # setting the new records which were added to the database after previous 
        # model train to back to 0 as a new model will be force retainined after load_data()
        self._new_recs = 0

        # loads data from the SQL database and pre-processes the data.
        self._df = utils.get_df_from_db()
        
        # fail safe to load data later when the database is empty
        if self._df.empty:
            self._new_recs = math.inf
            return
        self._shape = self._df.shape

        # replacing NA values in the dataframe with -1
        self._df.fillna(-1, inplace=True)

        self._X, self._y = utils.get_Xy(self._df)

        # pre processing of data
        self._X, tt_encoder = utils.ohe_feature(self._X, utils.TARGET_TYPE)
        self._encoders[utils.TARGET_TYPE] = tt_encoder

        self._y, ds_hash_encoder = utils.label_encode_feature(self._y, utils.DATASET_HASH)
        self._encoders[utils.DATASET_HASH] = ds_hash_encoder

    def train(self):
        # fail safe to train model later when the database is empty
        if self._new_recs == math.inf:
            return

        # fail safe to for first time training of model
        if self._df['index'].count() <= self.MAX_NEW_RECORDS:
            return

        # throws error if the data is not loaded before training.
        if self._X is None:
            raise RuntimeError('data not loaded! \n`call function `load_data()` before train()')

        # force reloading the data before training as the no of new records 
        # after the previous model was trained is >= MAX_NEW_RECORDS
        if self._new_recs >= self.MAX_NEW_RECORDS:
            self.load_data()
            self._new_recs = 0

        # since force retrain is possible
        self._retain = False

        X_train, X_test, y_train, y_test = train_test_split(self._X, self._y, test_size=0.2, random_state=123)
        
        self._model = KNeighborsClassifier()
        self._model.fit(X_train, y_train)

        self._model_create_time = datetime.now()
        
        y_pred = self._model.predict(X_test)
        self._accuracy = accuracy_score(y_test, y_pred)

    def load_data_and_train(self):
        self.load_data()
        self.train()

    def predict(self, X_pred):
        # check if the shape of the input df matches that used to train the model.
        if X_pred.shape[1] != self._X.shape[1]:
            raise RuntimeError('Input Shape miss match! aborting!')

        # force retrain of model if a set of new data records have been added to the model.
        # at this point reload the data and train the model.
        # or if the retrain flag is set to true because new data has been loaded
        if self._retain == True or self._new_recs >= self.MAX_NEW_RECORDS:
            self.train()

        y_pred = self._model.predict(X_pred)

        # decodes the predicted value using the inverse_transform method of the encoder.
        val = self._encoders[utils.DATASET_HASH].inverse_transform(y_pred)

        # creates and returns a dataframe containing the all the metric records
        # which match the predicted output of the model.    
        return self._df[self._df[utils.DATASET_HASH] == val[0]]   

    def _test(self, print_details=False):
        # this function tests the entire functionality without affecting the class variables
        # loads data from db, pre-processes it and trains a model and displays the 
        
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

        print('accuracy: ' + str(accuracy_score(y_test, y_pred)))

        if print_details:
            # kneighbors()[0] contains distances to points
            # kneighbors()[1] contains indcies of nearest points
            print(model.kneighbors(X_test)[1])

            print(y_test.to_string(header=False))
            print(pd.DataFrame(y_pred).to_string(header=False))
