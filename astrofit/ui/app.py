import tkinter as tk

from astrofit.ui.main_frame import MainFrame


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Moon Analyzer")

        main_frame = MainFrame(self)
        main_frame.mainloop()


if __name__ == '__main__':
    app = App()