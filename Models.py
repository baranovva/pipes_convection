import numpy as np
from pandas import read_csv
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from joblib import dump


class DataPreparing:
    def __init__(self, file_name: str):
        self.data = read_csv(filepath_or_buffer=file_name, header=0, sep=',')

    def split_data(self) -> object:
        samples = self.data.iloc[:, 0]
        targets = self.data.iloc[:, 1:]
        return samples, targets


class Models:
    def __init__(self, samples_train: object, targets_train: object):
        self.samples_train = samples_train.to_frame()
        self.targets_train = targets_train

    def regression(self) -> object:
        parameters = {'polynomialfeatures__degree': np.arange(1, 5)}
        search = GridSearchCV(make_pipeline(PolynomialFeatures(), LinearRegression()),
                              param_grid=parameters)
        search.fit(self.samples_train, self.targets_train)
        best_degree = search.best_params_['polynomialfeatures__degree']
        poly = PolynomialFeatures(degree=best_degree).fit_transform(self.samples_train)
        return LinearRegression(n_jobs=-1).fit(poly, self.targets_train), best_degree


path = 'data/water.csv'
samples, targets = DataPreparing(path).split_data()
regression, degree = Models(samples, targets).regression()
print(degree)
print(regression.coef_)
print(regression.intercept_)
if path == "data/air.csv":
    dump(regression, 'models/air.joblib')
else:
    dump(regression, 'models/water.joblib')
