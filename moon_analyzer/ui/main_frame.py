import os
import tkinter as tk
import tkinter.ttk as ttk

from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename

from moon_analyzer.core.coope_fit import coope_fit_method


class MainFrame(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        self.compute_btn = None
        self.status = tk.StringVar(self, "")
        self.image = None
        self.canvas = None

        self.points = {}
        self.ovals = {}

        self.shape = {}

        self._set_ui()

    def _set_ui(self):
        # Menu
        menu_bar = tk.Menu(self)

        menu_file = tk.Menu(menu_bar, tearoff=0)
        menu_file.add_command(label="Ouvrir une image", command=self._open_image)
        menu_file.add_command(label="Nettoyer le canvas", command=self._clean_canvas)
        menu_file.add_command(label="Quitter", command=self.quit)
        menu_bar.add_cascade(label="Fichier", menu=menu_file)

        self.master.config(menu=menu_bar)

        # Compute button
        self.compute_btn = ttk.Button(self, text="Calculer", command=self._on_compute, state=tk.DISABLED)
        self.compute_btn.pack()

        # Status bar
        tk.Label(self, textvariable=self.status, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

        self.pack(fill="both", expand=True)

    def _open_image(self):
        if self.canvas is not None:
            self._clean_canvas()
            self.canvas.pack_forget()
            self.canvas = None

        filename = askopenfilename(title="Choisissez une image", filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))

        if filename != "" and filename is not None and os.path.exists(filename):
            self.image = ImageTk.PhotoImage(Image.open(filename))
            self._set_canvas()

    def _set_canvas(self):
        if self.image is not None:
            self.canvas = tk.Canvas(self, width=self.image.width(), height=self.image.height(), bg="light yellow")
            self.canvas.create_image(self.image.width() / 2, self.image.height() / 2, image=self.image)
            self.canvas.bind("<Button-1>", self._on_left_click)
            self.canvas.bind("<Button-3>", self._on_right_click)
            self.canvas.pack()

    def _on_left_click(self, event):
        point = (event.x, event.y)
        hash = point.__hash__()

        if hash not in self.points.keys():
            self.points[hash] = point
            self.ovals[hash] = self.canvas.create_oval(event.x - 4, event.y - 4, event.x + 4, event.y + 4, fill="light green")

            self.status.set("X = {}; Y = {}".format(event.x, event.y))

            self._check_compute_btn_state()

    def _on_right_click(self, event):
        point = (event.x, event.y)
        hash = point.__hash__()
        delete = False

        if hash in self.points.keys():
            delete = True
        else:
            for h, p in self.points.items():
                if p[0] - 4 <= point[0] <= p[0] + 4 and p[1] - 4 <= point[1] <= p[1] + 4:
                    delete = True
                    hash = h
                    break

        if delete:
            self.points.pop(hash, None)
            self.canvas.delete(self.ovals[hash])
            self.ovals.pop(hash, None)
            self._check_compute_btn_state()

    def _check_compute_btn_state(self):
        if len(self.points) > 2:
            self.compute_btn.config(state=tk.NORMAL)
        else:
            self.compute_btn.config(state=tk.DISABLED)

    def _dispatch_coordinates(self):
        return [x[0] for x in self.points.values()], [y[1] for y in self.points.values()]

    def _on_compute(self):
        center, radius = coope_fit_method(*self._dispatch_coordinates())

        self.status.set("Rayon : {} pixels".format(radius))
        print("Centre : ({}; {})".format(*center))
        print(self.status.get())

        self._clean_shape()
        self.shape["outline"] = self.canvas.create_oval(center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius,
                                                        outline="red", width=2)
        self.shape["center"] = self.canvas.create_oval(center[0] - 4, center[1] - 4, center[0] + 4, center[1] + 4, fill="red")

    def _clean_shape(self):
        if "outline" in self.shape and self.shape["outline"] is not None:
            self.canvas.delete(self.shape["outline"])

        if "center" in self.shape and self.shape["center"] is not None:
            self.canvas.delete(self.shape["center"])

    def _clean_points(self):
        self.status.set("")
        self.points.clear()
        self.canvas.delete(*self.ovals.values())
        self.ovals.clear()

    def _clean_canvas(self):
        self._clean_points()
        self._clean_shape()
