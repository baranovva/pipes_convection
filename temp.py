import tkinter as tk
from tkinter import ttk, scrolledtext

from math import log, pi
from Nu import Nu
from Models import Material


def a(nusselt: float, lambd: float, d: float):
    # коэф теплоотдачи
    return nusselt * lambd / d


def calculate():
    """Функция для вычисления и вывода результатов в окно"""
    # начальные условия
    t_inlet = float(entry_t_inlet.get())
    t_out = float(entry_t_out.get())
    t_external = float(entry_t_external.get())
    d_in = float(entry_d_in.get())
    d_external = float(entry_d_external.get())
    v_external = float(entry_v_external.get())
    Re_in = float(entry_Re_in.get())
    path_external = entry_path_external.get()
    path_internal = entry_path_internal.get()
    is_gaz_external = True
    is_gaz_internal = False
    t_wall = t_external
    p_inlet = float(entry_p_inlet.get())
    p_external = float(entry_p_external.get())

    # Остальной код для вычислений оставляем без изменений
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
    a_external = a(nusselt=avg_Nu_external, lambd=material_external.lambd, d=d_external)  # коэф теплоотдачи внешний

    avg_Nu_in = Nu.NuInternal(Re=Re_in, Pr=material_in_avg.Pr, is_gaz=is_gaz_internal,
                              Mu=material_in_avg.Mu, Mu_wall=material_in_wall.Mu).calculate()  # Уонг стр 68
    a_in = a(nusselt=avg_Nu_in, lambd=material_in_avg.lambd, d=d_in)  # коэф теплоотдачи внутренний

    k_l = pi * (1 / (a_in * d_in) + log(d_external / d_in) / (2 * lambda_pipe) + 1 / (
            a_external * d_external)) ** -1  # линейный коэффициент теплоотдачи, Исаченко стр 37

    l = material_in_inlet.ro * v_in * material_in_inlet.c_p * pi * ((d_in / 2) ** 2) * (t_inlet - t_out) / (
            k_l * delta_T_ln)  # из уравнения теплового баланса
    ksi = 0.184 / (Re_in ** 0.2)  # коэф гидр потерь Исаченко стр 215
    delta_p = ksi * (l / d_in) * (0.5 * material_in_inlet.ro * v_in ** 2)  # перепад давления

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f'Re внешнего течения: {Re_external[0]:.6}\nV internal: {v_in[0]:.6}\n')
    output_text.insert(tk.END, f'delta_T_max: {delta_T_max:.6}\ndelta_T_min: {delta_T_min:.6}\n')
    output_text.insert(tk.END, f'delta_T_ln: {delta_T_ln:.6}\nt_avg: {t_avg:.6}\n')
    output_text.insert(tk.END, f'average Nu external: {avg_Nu_external[0]:.6}\na external: {a_external[0]:.6}\n')
    output_text.insert(tk.END, f'average Nu internal: {avg_Nu_in[0]:.6}\na internal: {a_in[0]:.6}\n')
    output_text.insert(tk.END, f'k_l: {k_l[0]:.6}\nksi: {ksi:.6}\n')
    output_text.insert(tk.END, f'Длина трубы: {l[0]:.6}\nПерепад давления: {delta_p[0]:.6}')


root = tk.Tk()
root.title("Конвекция 1.0.0")

# Создаем и размещаем элементы интерфейса
label_t_inlet = tk.Label(root, text="Температура входа, °C")
label_t_inlet.grid(row=0, column=0)
entry_t_inlet = tk.Scale(root, from_=0, to=100, orient="horizontal")
entry_t_inlet.set(80)
entry_t_inlet.grid(row=0, column=1)

label_t_out = tk.Label(root, text="Выходная температура, °C")
label_t_out.grid(row=1, column=0)
entry_t_out = tk.Entry(root)
entry_t_out.grid(row=1, column=1)
entry_t_out.insert(0, "50.5")

label_t_external = tk.Label(root, text="Температура внешней среды, °C")
label_t_external.grid(row=2, column=0)
entry_t_external = tk.Entry(root)
entry_t_external.grid(row=2, column=1)
entry_t_external.insert(0, "0")

label_t_wall = tk.Label(root, text="Температура стенки, °C")
label_t_wall.grid(row=3, column=0)
entry_t_wall = tk.Entry(root)
entry_t_wall.grid(row=3, column=1)
entry_t_wall.insert(0, "0")

label_p_inlet = tk.Label(root, text="Внутреннее входное давление, атм")
label_p_inlet.grid(row=4, column=0)
entry_p_inlet = tk.Entry(root)
entry_p_inlet.grid(row=4, column=1)
entry_p_inlet.insert(0, "1")

label_p_external = tk.Label(root, text="Внешнее давление, атм")
label_p_external.grid(row=5, column=0)
entry_p_external = tk.Entry(root)
entry_p_external.grid(row=5, column=1)
entry_p_external.insert(0, "1")

label_d_in = tk.Label(root, text="Внутренний диаметр трубы, м")
label_d_in.grid(row=6, column=0)
entry_d_in = tk.Entry(root)
entry_d_in.grid(row=6, column=1)
entry_d_in.insert(0, "0.014")

label_d_external = tk.Label(root, text="Внешний диаметр трубы, м")
label_d_external.grid(row=7, column=0)
entry_d_external = tk.Entry(root)
entry_d_external.grid(row=7, column=1)
entry_d_external.insert(0, "0.02")

label_v_external = tk.Label(root, text="Внешняя скорость течения, м/с")
label_v_external.grid(row=8, column=0)
entry_v_external = tk.Entry(root)
entry_v_external.grid(row=8, column=1)
entry_v_external.insert(0, "2")

label_Re_in = tk.Label(root, text="Re внутреннего течения")
label_Re_in.grid(row=9, column=0)
entry_Re_in = tk.Entry(root)
entry_Re_in.grid(row=9, column=1)
entry_Re_in.insert(0, "3426.606")

label_path_external = tk.Label(root, text="Путь к данным для наружной жидкости")
label_path_external.grid(row=10, column=0)
entry_path_external = ttk.Combobox(root, values=["data/water.csv", "data/air.csv"])
entry_path_external.grid(row=10, column=1)
entry_path_external.current(1)

label_path_internal = tk.Label(root, text="Путь к данным для внутренней жидкости")
label_path_internal.grid(row=12, column=0)
entry_path_internal = ttk.Combobox(root, values=["data/water.csv", "data/air.csv"])
entry_path_internal.grid(row=12, column=1)
entry_path_internal.current(0)

button_calculate = tk.Button(root, text="Вычислить", command=calculate)
button_calculate.grid(row=13, columnspan=2)

output_text = scrolledtext.ScrolledText(root, width=50, height=20, wrap=tk.WORD)
output_text.grid(row=14, columnspan=2)

root.mainloop()
