import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline


class DataPreparing:
    def __init__(self, file_name: str):
        self.data = pd.read_csv(filepath_or_buffer=file_name, header=0, sep=',')

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
                              param_grid=parameters, n_jobs=-1)
        search.fit(self.samples_train, self.targets_train)
        best_degree = search.best_params_['polynomialfeatures__degree']
        poly = PolynomialFeatures(degree=best_degree).fit_transform(self.samples_train)
        return LinearRegression(n_jobs=-1).fit(poly, self.targets_train), best_degree


class Material:
    def __init__(self, T, p, path):
        self.T = T
        self.p = p

        index = np.array(pd.read_csv(path, header=0, sep=',', usecols=[0]))

        if round(T) not in index:
            samples, targets = DataPreparing(path).split_data()
            regression, degree = Models(samples, targets).regression()
            material = regression.predict(self._temp(degree))
        else:
            index = np.where(index == round(T))[0]
            material = np.array(pd.read_csv(path, header=0, sep=',', usecols=range(1, 6), skiprows=index[0], nrows=1))

        if path == "data/air.csv":
            self.ro = p * material[:, 0]
        else:
            self.ro = material[:, 0]
        self.c_p = material[:, 1]
        self.lambd = material[:, 2]
        self.Pr = material[:, 3]
        self.Mu = material[:, 4]

    def _temp(self, PF_degree: float):
        return PolynomialFeatures(PF_degree).fit_transform(np.array([self.T]).reshape(-1, 1))
