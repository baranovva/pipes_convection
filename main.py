from math import log, pi
from Nu import Nu
from Models import Material


def a(Nusselt: float, lambd: float, d: float):
    # коэф теплоотдачи
    return Nusselt * lambd / d


'''Внутреняя жидкость - вода, внешняя - воздух. Обтекание поперечное'''
# начальные условия
path_external = 'data/air.csv'
path_internal = 'data/water.csv'
is_gaz_external = True
is_gaz_internal = False
t_inlet = 80.
t_out = 50.5
t_external = 0.
t_wall = t_external
p_inlet = 1.
p_external = 1.
d_in = 0.014
d_external = 0.02
v_external = 2.
Re_in = 3426.606

# теплопроводность трубы, ПП
lambda_pipe = 0.24

t_avg = (t_inlet + t_out) / 2
delta_T_max = max((t_inlet - t_external), (t_out - t_external))
delta_T_min = min((t_inlet - t_external), (t_out - t_external))
delta_T_ln = (delta_T_max - delta_T_min) / log(delta_T_max / delta_T_min)  # log профиль температуры

# свойства материалов при заданной температуре и давлении
material_external = Material(T=t_external, p=p_external, path=path_external)
material_in_wall = Material(T=t_wall, p=p_inlet, path=path_internal)
material_in_avg = Material(T=t_avg, p=p_inlet, path=path_internal)
material_in_inlet = Material(T=t_inlet, p=p_inlet, path=path_internal)

v_in = Re_in * material_in_inlet.Mu / (d_in * material_in_inlet.ro)  # скорость течения в трубе при заданном Re_in
Re_external = material_external.ro * v_external * d_external / material_external.Mu  # Re для внешнего течения

avg_Nu_external = Nu.NuExternal(Re=Re_external, Pr=material_external.Pr,
                                is_gaz=is_gaz_external).calculate()  # Уонг стр 72
a_external = a(Nusselt=avg_Nu_external, lambd=material_external.lambd, d=d_external)  # коэф теплоотдачи внешний

avg_Nu_in = Nu.NuInternal(Re=Re_in, Pr=material_in_avg.Pr, is_gaz=is_gaz_internal,
                          Mu=material_in_avg.Mu, Mu_wall=material_in_wall.Mu).calculate()  # Уонг стр 68
a_in = a(Nusselt=avg_Nu_in, lambd=material_in_avg.lambd, d=d_in)  # коэф теплоотдачи внутренний

k_l = pi * (1 / (a_in * d_in) + log(d_external / d_in) / (2 * lambda_pipe) + 1 / (
        a_external * d_external)) ** -1  # линейный коэффициент теплоотдачи, Исаченко стр 37

l = material_in_inlet.ro * v_in * material_in_inlet.c_p * pi * ((d_in / 2) ** 2) * (t_inlet - t_out) / (
        k_l * delta_T_ln)  # из уравнения теплового баланса
ksi = 0.184 / (Re_in ** 0.2)  # коэф гидр потерь Исаченко стр 215
delta_p = ksi * (l / d_in) * (0.5 * material_in_inlet.ro * v_in ** 2)  # перепад давления

print(f'Re external: {Re_external[0]:.6}, V internal: {v_in[0]:.6}')
print(f'delta_T_max: {delta_T_max:.6}, delta_T_min: {delta_T_min:.6}, delta_T_ln: {delta_T_ln:.6}, t_avg: {t_avg:.6}')
print(f'average Nu external: {avg_Nu_external[0]:.6}, a external: {a_external[0]:.6}')
print(f'average Nu internal: {avg_Nu_in[0]:.6}, a internal: {a_in[0]:.6}')
print(f'k_l: {k_l[0]:.6}, ksi: {ksi:.6}')
print(f'l: {l[0]:.6}, delta_p: {delta_p[0]:.6}')
