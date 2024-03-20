def radiation(T_wall, eps):
    sigma = 5.670374419e-8
    return 4 * eps * sigma * (T_wall + 273.15) ** 3
