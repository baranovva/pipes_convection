import numpy as np
from math import log, pi
from Nu import Nu
from Models import Models, DataPreparing
from sklearn.preprocessing import PolynomialFeatures


def a(Nusselt, lambd, d):
    # коэф теплоотдачи
    return Nusselt * lambd / d


'''Внутреняя жидкость - вода, внешняя - воздух. Обтекание поперечное'''
# начальные условия
t_in = 80
t_out = 50.5
t_avg = 0.5*(t_in + t_out)
t_external = 0
is_gaz_external = True
is_gaz_internal = False
d_in = 0.014
d_external = 0.02
v_external = 2
Re_in = 3426.606

# теплопроводность трубы, ПП
lambda_pipe = 0.24

# воздух 0 С, 1 атм
Mu_external = 1.72e-5
ro_external = 1.293
lambda_external = 0.0244

# "ro"	"c_p"	"lambda" 	"Pr"	"Mu"
samples, targets = DataPreparing('water.csv').split_data()
models = Models(samples, targets)
regression, degree = models.regression()

# вода t = 0 С, 3 atm
Mu_in_0 = regression.predict(PolynomialFeatures(degree).fit_transform(np.array([0]).reshape(-1, 1)))[:, 4]  # 1.79e-3

# вода t средняя С, 3 atm
lambda_in_70 = regression.predict(PolynomialFeatures(degree).fit_transform(np.array([t_avg]).reshape(-1, 1)))[:, 2]# 0.668
Pr_in_70 = regression.predict(PolynomialFeatures(degree).fit_transform(np.array([t_avg]).reshape(-1, 1)))[:, 3]# 2.55
Mu_in_70 = regression.predict(PolynomialFeatures(degree).fit_transform(np.array([t_avg]).reshape(-1, 1)))[:, 4]# 4.06e-4

# вода t = 80 С, 3 atm
ro_in_80 = regression.predict(PolynomialFeatures(degree).fit_transform(np.array([t_in]).reshape(-1, 1)))[:, 0] # 971.08
c_p_80 = regression.predict(PolynomialFeatures(degree).fit_transform(np.array([t_in]).reshape(-1, 1)))[:, 1] # 4195
Mu_in_80 = regression.predict(PolynomialFeatures(degree).fit_transform(np.array([t_in]).reshape(-1, 1)))[:, 4] # 3.54E-04

v = Re_in * Mu_in_80 / (d_in * ro_in_80)  # скорость течения в трубе при заданном Re_in
Re_external = ro_external * v_external * d_external / Mu_external  # Re для внешнего течения

delta_T_max = max((t_in - t_external), (t_out - t_external))
delta_T_min = min((t_in - t_external), (t_out - t_external))
delta_T_ln = (delta_T_max - delta_T_min) / log(delta_T_max / delta_T_min)  # log профиль температуры

av_Nu_out = Nu.NuExternal(Re=Re_external, is_gaz=is_gaz_external).calculate()  # Уонг стр 72
a_out = a(Nusselt=av_Nu_out, lambd=lambda_external, d=d_external)  # коэф теплоотдачи внешний

av_Nu_in = Nu.NuInternal(Re=Re_in, Pr=Pr_in_70, is_gaz=is_gaz_internal,
                         Mu=Mu_in_70, Mu_wall=Mu_in_0).calculate()  # Уонг стр 68
a_in = a(Nusselt=av_Nu_in, lambd=lambda_in_70, d=d_in)  # коэф теплоотдачи внутренний

k_l = (1 / (a_in * pi * d_in) + log(d_external / d_in) / (2 * pi * lambda_pipe) + 1 / (
        a_out * pi * d_external)) ** -1  # линейный коэффициент теплоотдачи, Исаченко стр 37

l = ro_in_80 * v * c_p_80 * pi * ((d_in / 2) ** 2) * (t_in - t_out) / (
        k_l * delta_T_ln)  # из уравнения теплового баланса
delta_p = 0.184 / (Re_in ** 0.2) * (l / d_in) * (
        ro_in_80 * v * v / 2)  # перепад давления, коэф гидр потерь Исаченко стр 215

print(f'Re external: {Re_external}, V external: {v_external}')
print(f'Re internal: {Re_in}, V internal: {v}')
print(f'delta_T_max: {delta_T_max}, delta_T_min: {delta_T_min}, delta_T_ln: {delta_T_ln}')
print(f'average Nu external: {av_Nu_out}, a external: {a_out}')
print(f'average Nu internal: {av_Nu_in}, a internal: {a_in}')
print(f'k_l: {k_l}')
print(f'l: {l}, delta_p: {delta_p}')
