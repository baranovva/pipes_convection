import numpy as np

from pandas import read_csv
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error


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
                              param_grid=parameters, n_jobs=-1, cv=5)
        search.fit(self.samples_train, self.targets_train)
        best_degree = search.best_params_['polynomialfeatures__degree']
        poly = PolynomialFeatures(degree=best_degree).fit_transform(self.samples_train)
        model = LinearRegression(n_jobs=-1)
        return model.fit(poly, self.targets_train), best_degree


'''samples_train, targets_train = DataPreparing('water.csv').split_data()
models = Models(samples_train, targets_train)

regression, degree = models.regression()
predictions = regression.predict(PolynomialFeatures(degree=degree).fit_transform(samples_train.to_frame()))
print(predictions)
print(f'RMSE: {np.sqrt(mean_squared_error(targets_train, predictions))}')
print(degree)'''

'''samples_train, targets_train = DataPreparing('air.csv').split_data()
models = Models(samples_train, targets_train)

regression, degree = models.regression()
predictions = regression.predict(PolynomialFeatures(degree=degree).fit_transform(samples_train.to_frame()))
print(predictions)
print(f'RMSE: {np.sqrt(mean_squared_error(targets_train, predictions))}')
print(degree)'''
