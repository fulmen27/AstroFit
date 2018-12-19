import os
import tkinter as tk
import tkinter.ttk as ttk

from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename

from astrofit.core.adjust_position import adjust_position
from astrofit.core.coope_fit import coope_fit_method
from astrofit.core.plot import show_plot
from astrofit.core.threshold import threshold_image


class MainFrame(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        self.compute_btn = None
        self.status = tk.StringVar(self, "")
        self.image = {}
        self.magnet = tk.BooleanVar(self, True)
        self.threshold = tk.BooleanVar(self, False)
        self.threshold_value = tk.IntVar(self, 128)
        self.canvas = None

        self.points = {}
        self.ovals = {}

        self.shape = {}

        self._set_ui()
        self._open_image()

    def _set_ui(self):
        # Geometry
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Menu
        menu_bar = tk.Menu(self)

        menu_file = tk.Menu(menu_bar, tearoff=0)
        menu_file.add_command(label="Ouvrir une image", command=self._open_image)
        menu_file.add_command(label="Nettoyer le canvas", command=self._clean_canvas)
        menu_file.add_command(label="Quitter", command=self.quit)
        menu_bar.add_cascade(label="Fichier", menu=menu_file)

        self.master.config(menu=menu_bar)

        # Buttons
        buttons_frame = ttk.Frame(self)

        # ttk.Button(buttons_frame, text="Points automatiques", command=self._auto_points, state=tk.NORMAL).pack(fill=tk.BOTH)

        self.compute_btn = ttk.Button(buttons_frame, text="Calculer", command=self._on_compute, state=tk.DISABLED)
        self.compute_btn.pack(fill=tk.BOTH)

        self.plot_btn = ttk.Button(buttons_frame, text="Plot", command=self._on_plot, state=tk.DISABLED)
        self.plot_btn.pack(fill=tk.BOTH)

        ttk.Checkbutton(buttons_frame, text="Aimant", variable=self.magnet).pack(fill=tk.BOTH)

        ttk.Checkbutton(buttons_frame, text="Seuillage", variable=self.threshold, command=self._on_threshold).pack(fill=tk.BOTH)
        ttk.Spinbox(buttons_frame, from_=0, to=255, textvariable=self.threshold_value, command=self._on_threshold_value).pack(fill=tk.BOTH)

        buttons_frame.grid(column=1, row=0, sticky="nsew")

        # Status bar
        tk.Label(self, textvariable=self.status, bd=1, relief=tk.SUNKEN, anchor=tk.W).grid(column=0, row=2, columnspan=2, sticky="sew")

        self.grid(column=0, row=0, sticky="nsew")

    def _open_image(self):
        if self.canvas is not None:
            self._clean_canvas()
            self.canvas.pack_forget()
            self.canvas = None

        filename = askopenfilename(title="Choisissez une image", filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))

        if filename != "" and filename is not None and os.path.exists(filename):
            self.image["filename"] = filename
            self.image["pil"] = Image.open(filename)
            self.image["photo"] = ImageTk.PhotoImage(self.image["pil"])
            self.image["threshold_static"] = threshold_image(self.image["pil"], 100)  # Utilisé pour placer les points précisément
            self._set_canvas()

    def _set_canvas(self):
        if "photo" in self.image and self.image["photo"] is not None:
            photo = self.image["photo"]
            self.canvas = tk.Canvas(self, width=photo.width(), height=photo.height(), bg="light yellow")
            self.image["canvas"] = self.canvas.create_image(photo.width() / 2, photo.height() / 2, image=photo)
            self.canvas.bind("<Button-1>", self._on_left_click)
            self.canvas.bind("<Button-3>", self._on_right_click)
            self.canvas.grid(column=0, row=0, sticky="nsew")

    def _on_left_click(self, event):
        x, y = adjust_position(event.x, event.y, self.image["threshold_static"]) if self.magnet.get() else (event.x, event.y)

        if self._add_point(x, y, "lawn green"):
            self.status.set("X = {}; Y = {}".format(x, y))

    def _auto_points(self):
        points = ([255, 255], [355, 355])
        for point in points:
            self._add_point(point[0], point[1], "cyan")

    def _add_point(self, x, y, color):
        point = (x, y)
        hash_point = point.__hash__()

        if hash_point not in self.points.keys():
            self.points[hash_point] = point
            self.ovals[hash_point] = self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color)
            self._check_compute_btn_state()

            return True
        return False

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

        self.status.set("Rayon : {} pixels, Centre : ({}, {})".format(radius, *center))
        print("Centre : ({}; {})".format(*center))
        print(self.status.get())

        self._clean_shape()
        self.shape["outline"] = self.canvas.create_oval(center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius,
                                                        outline="red", width=2)
        self.shape["center_oval"] = self.canvas.create_oval(center[0] - 4, center[1] - 4, center[0] + 4, center[1] + 4, fill="red")

        self.shape["radius"] = radius
        self.shape["center"] = center
        self.plot_btn.config(state=tk.NORMAL)

    def _on_plot(self):
        show_plot(self.shape["radius"], *self.shape["center"], self.points, self.image["pil"].size, self.image["filename"])

    def _clean_shape(self):
        if "outline" in self.shape and self.shape["outline"] is not None:
            self.canvas.delete(self.shape["outline"])

        if "center_oval" in self.shape and self.shape["center_oval"] is not None:
            self.canvas.delete(self.shape["center_oval"])
        self.plot_btn.config(state=tk.DISABLED)

    def _clean_points(self):
        self.status.set("")
        self.points.clear()
        self.canvas.delete(*self.ovals.values())
        self.ovals.clear()

        self._check_compute_btn_state()

    def _clean_canvas(self, clean_image=False):
        self._clean_points()
        self._clean_shape()

        if clean_image:
            self.canvas.delete(self.image["canvas"])

    def _change_image(self):
        self.canvas.itemconfig(self.image["canvas"], image=self.image["photo"])

    def _on_threshold(self):
        if self.canvas is not None and "pil" in self.image:
            if self.threshold.get():
                self.image["photo"] = ImageTk.PhotoImage(threshold_image(self.image["pil"], self.threshold_value.get()))
            else:
                self.image["pil"] = Image.open(self.image["filename"])
                self.image["photo"] = ImageTk.PhotoImage(self.image["pil"])

        self._change_image()

    def _on_threshold_value(self):
        if self.threshold.get():  # On ne réactualise pas l'image inutilement si on est pas en mode seuillage.
            self._on_threshold()
