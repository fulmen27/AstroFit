import numpy as np

from scipy import optimize as opt


def coope_fit_method(x, y):
    x = np.array(x)
    y = np.array(y)

    def my_model(coefficients):
        return coefficients[0] * x + coefficients[1] * y + coefficients[2]

    def residuals(coefficients):
        return x ** 2 + y ** 2 - my_model(coefficients)

    solution = opt.leastsq(residuals, np.zeros(3))[0]
    center = (solution[0] / 2, solution[1] / 2)
    radius = np.sqrt(solution[2] + center[0] ** 2 + center[1] ** 2)

    return center, radius