import numpy as np 
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

x = np.arange(0, 10, .1)  # [0. .1, ..., 9.9]
y = np.pi*x**2 + np.e  # y = pi*x^2 + e
y += np.random.randn(len(x))  # add noise to data

fig, ax = plt.subplots()
ax.plot(x, y, 'kx', label='Raw data')

def f(x, a, b, n):
    # x: independent variable
    # a, b, n: fitting parameters
    return a + b*x**n

popt, pcov = curve_fit(f=f, xdata=x, ydata=y, p0=[1, 1, 1])
print(popt)

a, b, n = popt
ax.plot(x, f(x, a, b, n), 'r-', label='Fitted curve')

ax.legend()

plt.show()
