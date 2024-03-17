import numpy as np
import pandas as pd


class Material:
    def __init__(self, T, p, path):
        self.T = T
        self.p = p
        self.path = 'data/' + path + '.csv'

        index_df = pd.read_csv(self.path, header=0, sep=',', usecols=[0])
        index = np.array(index_df.iloc[:, 0])

        if round(T) not in index:
            if self.path == "data/air.csv":
                material = np.array([[1.14863908e+00 - 1.00173006e-03 * self.T,
                                      1.00038710e+00 + 1.80239309e-04 * self.T,
                                      2.59354842e-02 + 5.68095724e-05 * self.T,
                                      6.96383828e-01 + 1.12186761e-05 * self.T,
                                      1.83077369e-05 + 3.17467401e-08 * self.T]])
            else:
                material = np.array([[
                    9.99904895e+02 + 4.79079255e-02 * self.T - 7.34644522e-03 * self.T ** 2 + 3.85198135e-05 * self.T ** 3 - 1.13636364e-07 * self.T ** 4,
                    4.21137063e+03 - 2.21987180e+00 * self.T - 3.99970863e-02 * self.T ** 2 - 2.41841493e-04 * self.T ** 3 + 7.28438232e-07 * self.T ** 4,
                    5.49594406e-01 + 3.09203575e-03 * self.T - 4.05128206e-05 * self.T ** 2 + 5.02719504e-07 * self.T ** 3 - 2.91375292e-09 * self.T ** 4,
                    1.36158042e+01 - 4.80388307e-01 * self.T + 9.11797787e-03 * self.T ** 2 - 8.62917640e-05 * self.T ** 3 + 3.13228439e-07 * self.T ** 4,
                    1.78458741e-03 - 5.51527196e-05 * self.T + 9.83193475e-07 * self.T ** 2 - 9.03108005e-09 * self.T ** 3 + 3.22843824e-11 * self.T ** 4]])
        else:
            index = np.where(index == round(T))[0]
            material_df = pd.read_csv(self.path, header=0, sep=',', usecols=range(1, 6), skiprows=index[0], nrows=1)
            material = np.array(material_df)

        self.ro = material[:, 0]
        if self.path == "data/air.csv":
            self.ro *= p
        self.c_p = material[:, 1]
        self.lambd = material[:, 2]
        self.Pr = material[:, 3]
        self.Mu = material[:, 4]
