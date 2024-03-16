import tkinter as tk
from webbrowser import open_new


def show_error_popup(error_msg):
    popup = tk.Tk()
    popup.title("Ошибка")
    label = tk.Label(popup, text=error_msg)
    label.pack()
    button = tk.Button(popup, text="OK", command=popup.destroy)
    button.pack()
    popup.mainloop()


def open_link():
    open_new("https://github.com/baranovva/pipes_convection")


def show_about():
    popup = tk.Tk()
    popup.title("About")
    name = tk.Label(popup,
                    text='Расчет длины трубы и перепада давления в условиях вынужденной конвекции\n Трубы круглого сечения для воздуха и/или воды')
    name.pack()
    license = tk.Label(popup, text='License: MIT')
    license.pack()
    code = tk.Label(popup, text='Source code (github.com)', fg="blue", cursor="hand2")
    code.pack()
    code.bind("<Button-1>", open_link)
    button = tk.Button(popup, text="OK", command=popup.destroy)
    button.pack()
    popup.mainloop()
