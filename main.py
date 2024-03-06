import numpy as np
from math import log, pi

import pandas as pd

from Nu import Nu
from Models import Models, DataPreparing
from sklearn.preprocessing import PolynomialFeatures


def a(Nusselt: float, lambd: float, d: float):
    # коэф теплоотдачи
    return Nusselt * lambd / d


class Material:
    def __init__(self, T, p, path):
        self.T = T
        self.p = p

        if int(T) not in range(0, 110, 10):
            samples, targets = DataPreparing(path).split_data()
            regression, degree = Models(samples, targets).regression()
            material = regression.predict(self.temp(degree))
        else:
            index = np.array(pd.read_csv(path, header=0, sep=',', usecols=[0]))
            index = np.where(index == int(T))[0]
            material = np.array(pd.read_csv(path, header=0, sep=',', usecols=range(1, 6), skiprows=index[0], nrows=1))

        self.ro = material[:, 0]
        self.c_p = material[:, 1]
        self.lambd = material[:, 2]
        self.Pr = material[:, 3]
        self.Mu = material[:, 4]

    def temp(self, PF_degree: float):
        return PolynomialFeatures(PF_degree).fit_transform(np.array([self.T]).reshape(-1, 1))


'''Внутреняя жидкость - вода, внешняя - воздух. Обтекание поперечное'''
# начальные условия
path_external = 'air.csv'
path_internal = 'water.csv'
is_gaz_external = True
is_gaz_internal = False
t_inlet = 80
t_out = 50.5
t_external = 0
t_wall = t_external
p_inlet = 1
p_external = 1
d_in = 0.014
d_external = 0.02
v_external = 2
Re_in = 3426.606

# теплопроводность трубы, ПП
lambda_pipe = 0.24

# воздух 0 С, 1 атм
material_external = Material(T=t_external, p=p_external, path=path_external)
ro_external = material_external.ro  # 1.293
lambda_external = material_external.lambd  # 0.0244
Pr_external = material_external.Pr  # 0.707
Mu_external = material_external.Mu  # 1.72e-5

# вода t = стенки С
material_external_wall = Material(T=t_wall, p=p_inlet, path=path_internal)
Mu_in_wall = material_external_wall.Mu  # 1.79e-3

# вода t = средняя С
t_avg = 0.5 * (t_inlet + t_out)
material_external_avg = Material(T=t_avg, p=p_inlet, path=path_internal)
lambda_in_avg = material_external_avg.lambd  # 0.668
Pr_in_avg = material_external_avg.Pr  # 2.55
Mu_in_avg = material_external_avg.Mu  # 4.06e-4

# вода t = входная С
material_external_inlet = Material(T=t_inlet, p=p_inlet, path=path_internal)
ro_in_inlet = material_external_inlet.ro  # 971.08
c_p_inlet = material_external_inlet.c_p  # 4195
Mu_in_inlet = material_external_inlet.Mu  # 3.54E-04

v_in = Re_in * Mu_in_inlet / (d_in * ro_in_inlet)  # скорость течения в трубе при заданном Re_in
Re_external = ro_external * v_external * d_external / Mu_external  # Re для внешнего течения

delta_T_max = max((t_inlet - t_external), (t_out - t_external))
delta_T_min = min((t_inlet - t_external), (t_out - t_external))
delta_T_ln = (delta_T_max - delta_T_min) / log(delta_T_max / delta_T_min)  # log профиль температуры

av_Nu_out = Nu.NuExternal(Re=Re_external, Pr=Pr_external, is_gaz=is_gaz_external).calculate()  # Уонг стр 72
a_out = a(Nusselt=av_Nu_out, lambd=lambda_external, d=d_external)  # коэф теплоотдачи внешний

av_Nu_in = Nu.NuInternal(Re=Re_in, Pr=Pr_in_avg, is_gaz=is_gaz_internal,
                         Mu=Mu_in_avg, Mu_wall=Mu_in_wall).calculate()  # Уонг стр 68
a_in = a(Nusselt=av_Nu_in, lambd=lambda_in_avg, d=d_in)  # коэф теплоотдачи внутренний

k_l = pi * (1 / (a_in * d_in) + log(d_external / d_in) / (2 * lambda_pipe) + 1 / (
        a_out * d_external)) ** -1  # линейный коэффициент теплоотдачи, Исаченко стр 37

l = ro_in_inlet * v_in * c_p_inlet * pi * ((d_in / 2) ** 2) * (t_inlet - t_out) / (
        k_l * delta_T_ln)  # из уравнения теплового баланса
ksi = 0.184 / (Re_in ** 0.2)
delta_p = ksi * (l / d_in) * (0.5 * ro_in_inlet * v_in ** 2)  # перепад давления, коэф гидр потерь Исаченко стр 215

print(f'Re external: {Re_external}, V external: {v_external}')
print(f'Re internal: {Re_in}, V internal: {v_in}')
print(f'delta_T_max: {delta_T_max}, delta_T_min: {delta_T_min}, delta_T_ln: {delta_T_ln}')
print(f'average Nu external: {av_Nu_out}, a external: {a_out}')
print(f'average Nu internal: {av_Nu_in}, a internal: {a_in}')
print(f'k_l: {k_l}, ksi: {ksi}')
print(f'l: {l}, delta_p: {delta_p}')
