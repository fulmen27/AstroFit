import matplotlib.pyplot as plt
import pylab as pl
import os


def show_plot(radius, xc, yc, points, size, path):
    name = os.path.basename(path)
    x = []
    y = []
    for key, value in points.items():
        x.append(value[0])
        y.append(value[1])

    fig = plt.gcf()
    ax = plt.gca()
    ax.set_aspect(1)

    ax.set_xlim(0, size[0])
    ax.set_ylim(0, size[1])
    ax.set_xlabel("width")
    ax.set_ylabel("height")

    plt.title("Fit of image {}".format(name))

    circle = plt.Circle((xc, yc), radius=radius, fill=False, color='red')
    plt.plot(x, y)
    plt.plot([xc, xc+radius], [yc, yc], color='red', label=r'Radius = {}'.format(round(radius, 2)))
    pl.scatter(xc, yc, color='green', label=r'center = ({}, {})'.format(round(xc, 2), round(yc, 2)))
    ax.add_artist(circle)

    plt.legend()

    plt.show()
    fig.savefig("FIT_{}".format(name))
