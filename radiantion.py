def radiation(T_wall):
    sigma = 5.670367e-8
    eps = 0.5
    return 4 * eps * sigma * (T_wall + 273.15) ** 3
