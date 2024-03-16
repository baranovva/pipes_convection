import tkinter as tk


def show_error_popup(error_msg):
    popup = tk.Tk()
    popup.title("Ошибка")
    label = tk.Label(popup, text=error_msg)
    label.pack()
    button = tk.Button(popup, text="OK", command=popup.destroy)
    button.pack()
    popup.mainloop()


def show_about():
    popup = tk.Tk()
    popup.title("About")
    name = tk.Label(popup, text='Расчет длины трубы и перепада давления в условиях вынужденной конвекции\n Трубы круглого сечения для воздуха и/или воды')
    name.pack()
    license = tk.Label(popup, text='License: MIT')
    license.pack()
    code = tk.Label(popup, text='Source code: https://github.com/baranovva/pipes_convection')
    code.pack()
    button = tk.Button(popup, text="OK", command=popup.destroy)
    button.pack()
    popup.mainloop()
