import tkinter as tk
from tkinter import ttk, scrolledtext, BooleanVar, Checkbutton
from math import log, pi
from Nu import Nu
from Models import Material
from buttons import show_error_popup, show_about
from radiantion import radiation


def a(nusselt: float, lambd: float, d: float):
    # коэф теплоотдачи
    return nusselt * lambd / d


def calculate():
    path_external = 'data/' + entry_path_external.get() + '.csv'
    path_internal = 'data/' + entry_path_internal.get() + '.csv'
    is_use_radiation = rad.get()

    is_gaz_external = True
    is_gaz_internal = True
    if path_external == 'data/water.csv':
        is_gaz_external = False
    if path_internal == 'data/water.csv':
        is_gaz_internal = False

    t_inlet = float(entry_t_inlet.get())
    t_out = float(entry_t_out.get())
    t_external = float(entry_t_external.get())

    if is_gaz_internal and (t_inlet < -50 or t_inlet > 1200):
        show_error_popup('Неверная входная температура (-50 C < T < 1200 C)')
    if is_gaz_external and (t_external < -50 or t_inlet > 1200):
        show_error_popup('Неверная внешняя температура (-50 C < T < 1200 C)')
    if not is_gaz_internal and (t_inlet < 0 or t_inlet > 100):
        show_error_popup('Неверная входная температура (0 C < T < 100 C)')
    if is_gaz_external and (t_external < 0 or t_inlet > 100):
        show_error_popup('Неверная внешняя температура (0 C < T < 100 C)')

    if (t_out > t_inlet and t_external < t_inlet) or (t_out < t_inlet and t_external > t_inlet):
        show_error_popup('Указанная выходная температура недостижима')

    d_in = float(entry_d_in.get())
    d_external = float(entry_d_external.get())
    if d_in >= d_external or d_in == 0:
        show_error_popup('Неверные размеры трубы')

    v_external = float(entry_v_external.get())
    v_in = float(entry_v_in.get())
    if v_in <= 0 or v_external <= 0 or v_in > 3e+8 or v_external > 3e+8:
        show_error_popup('Неверное значение скорости')

    p_inlet = float(entry_p_inlet.get())
    p_external = float(entry_p_external.get())
    if p_inlet <= 0 or p_external <= 0:
        show_error_popup('Неверное значение давления')

    lambda_pipe = float(entry_lambda_pipe.get())
    if lambda_pipe <= 0:
        show_error_popup('Неверное значение теплопроводности трубы')

    t_avg = (t_inlet + t_out) / 2
    t_wall = (t_external + t_avg) / 2
    delta_T_max = max((t_inlet - t_external), (t_out - t_external))
    delta_T_min = min((t_inlet - t_external), (t_out - t_external))
    delta_T_ln = (delta_T_max - delta_T_min) / log(delta_T_max / delta_T_min)  # log профиль температуры

    # свойства материалов при заданной температуре и давлении
    material_external = Material(T=t_external, p=p_external, path=path_external)
    material_in_wall = Material(T=t_wall, p=p_inlet, path=path_internal)
    material_in_avg = Material(T=t_avg, p=p_inlet, path=path_internal)
    material_in_inlet = Material(T=t_inlet, p=p_inlet, path=path_internal)

    Re_in = material_in_avg.ro * v_in * d_in / material_in_avg.Mu
    Re_external = material_external.ro * v_external * d_external / material_external.Mu  # Re для внешнего течения

    avg_Nu_external = Nu.NuExternal(Re=Re_external, Pr=material_external.Pr,
                                    is_gaz=is_gaz_external).calculate()  # Уонг стр 72
    a_external = a(nusselt=avg_Nu_external, lambd=material_external.lambd, d=d_external)  # коэф теплоотдачи внешний

    if is_use_radiation and is_gaz_external:
        a_external += radiation(t_wall)

    avg_Nu_in = Nu.NuInternal(Re=Re_in, Pr=material_in_avg.Pr, is_gaz=is_gaz_internal,
                              Mu=material_in_avg.Mu, Mu_wall=material_in_wall.Mu).calculate()  # Уонг стр 68
    a_in = a(nusselt=avg_Nu_in, lambd=material_in_avg.lambd, d=d_in)  # коэф теплоотдачи внутренний

    k_l = pi * (1 / (a_in * d_in) + log(d_external / d_in) / (2 * lambda_pipe) + 1 / (
            a_external * d_external)) ** -1  # линейный коэффициент теплоотдачи, Исаченко стр 37

    l = material_in_inlet.ro * v_in * material_in_inlet.c_p * pi * ((d_in / 2) ** 2) * (t_inlet - t_out) / (
            k_l * delta_T_ln)  # из уравнения теплового баланса
    ksi = 0.184 / (Re_in ** 0.2)  # коэф гидр потерь Исаченко стр 215
    delta_p = ksi * (l / d_in) * (0.5 * material_in_inlet.ro * v_in ** 2)

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f'Re внешнего течения: {Re_external[0]:.6}\nRe внутренного течения: {Re_in[0]:.6}\n')
    output_text.insert(tk.END, f'delta_T_max: {delta_T_max:.6} °C\ndelta_T_min: {delta_T_min:.6} °C\n')
    output_text.insert(tk.END, f'delta_T_ln: {delta_T_ln:.6}\navarage T: {t_avg:.6} °C\nwall T: {t_wall:.6} °C\n')
    output_text.insert(tk.END,
                       f'average Nu external: {avg_Nu_external[0]:.6}\na external: {a_external[0]:.6} Вт/(м^2·K)\n')
    output_text.insert(tk.END, f'average Nu internal: {avg_Nu_in[0]:.6}\na internal: {a_in[0]:.6} Вт/(м^2·K)\n')
    output_text.insert(tk.END,
                       f'Линейный коэффциент теплопередачи: {k_l[0]:.6} Вт/(м·K)\nКоэффицент гидравлических потерь: {ksi[0]:.6}\n')
    output_text.insert(tk.END, f'Длина трубы: {l[0]:.6} м\nПерепад давления: {delta_p[0]:.6} Па')


root = tk.Tk()
root.title("Конвекция 1.1.0")

# создаем и размещаем элементы интерфейса
label_t_inlet = tk.Label(root, text="Входная температура, °C")
label_t_inlet.grid(row=0, column=0)
entry_t_inlet = tk.Entry(root)
entry_t_inlet.grid(row=0, column=1)
entry_t_inlet.insert(0, "80")

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

label_p_inlet = tk.Label(root, text="Внутреннее входное давление, атм")
label_p_inlet.grid(row=3, column=0)
entry_p_inlet = tk.Entry(root)
entry_p_inlet.grid(row=3, column=1)
entry_p_inlet.insert(0, "1")

label_p_external = tk.Label(root, text="Внешнее давление, атм")
label_p_external.grid(row=4, column=0)
entry_p_external = tk.Entry(root)
entry_p_external.grid(row=4, column=1)
entry_p_external.insert(0, "1")

label_d_in = tk.Label(root, text="Внутренний диаметр трубы, м")
label_d_in.grid(row=5, column=0)
entry_d_in = tk.Entry(root)
entry_d_in.grid(row=5, column=1)
entry_d_in.insert(0, "0.014")

label_d_external = tk.Label(root, text="Внешний диаметр трубы, м")
label_d_external.grid(row=6, column=0)
entry_d_external = tk.Entry(root)
entry_d_external.grid(row=6, column=1)
entry_d_external.insert(0, "0.02")

label_v_external = tk.Label(root, text="Скорость внешнего течения, м/с")
label_v_external.grid(row=7, column=0)
entry_v_external = tk.Entry(root)
entry_v_external.grid(row=7, column=1)
entry_v_external.insert(0, "2")

label_v_in = tk.Label(root, text="Скорость внутреннего течения, м/с")
label_v_in.grid(row=8, column=0)
entry_v_in = tk.Entry(root)
entry_v_in.grid(row=8, column=1)
entry_v_in.insert(0, "0.089")

label_lambda_pipe = tk.Label(root, text="Теплопроводность трубы, Вт/(м·K)")
label_lambda_pipe.grid(row=9, column=0)
entry_lambda_pipe = tk.Entry(root)
entry_lambda_pipe.grid(row=9, column=1)
entry_lambda_pipe.insert(0, "0.24")

label_path_external = tk.Label(root, text="Наружная жидкость")
label_path_external.grid(row=10, column=0)
entry_path_external = ttk.Combobox(root, values=["water", "air"])
entry_path_external.grid(row=10, column=1)
entry_path_external.current(1)

label_path_internal = tk.Label(root, text="Внутренняя жидкость")
label_path_internal.grid(row=11, column=0)
entry_path_internal = ttk.Combobox(root, values=["water", "air"])
entry_path_internal.grid(row=11, column=1)
entry_path_internal.current(0)

label_rad = tk.Label(root, text="Учитывать излучение")
label_rad.grid(row=12, column=0)
rad = BooleanVar()
entry_rad = Checkbutton(root, variable=rad)
entry_rad.grid(row=12, column=1)

button_calculate = tk.Button(root, text="Calculate", command=calculate)
button_calculate.grid(row=13, columnspan=2)

output_text = scrolledtext.ScrolledText(root, width=50, height=15, wrap=tk.WORD)
output_text.grid(row=14, columnspan=2)

button_clear = tk.Button(root, text="About", command=show_about)
button_clear.grid(row=15, columnspan=2)

root.mainloop()
