# Double pendulum formula translated from the C code at
# http://www.physics.usyd.edu.au/~wheat/dpend_html/solve_dpend.c

from typing import List, Sequence

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import scipy.integrate as integrate
from numpy import cos, pi, sin

G = 9.8  # acceleration due to gravity, in m/s^2
L1 = 1.0  # length of pendulum 1 in m
L2 = 1.0  # length of pendulum 2 in m
M1 = 1.0  # mass of pendulum 1 in kg
M2 = 1.0  # mass of pendulum 2 in kg


def derivatives(state: Sequence[float], _) -> List[float]:
    dydx: List[float] = [0, 0, 0, 0]
    dydx[0] = state[1]

    delta = state[2] - state[0]
    denominator = (M1 + M2) * L1 - M2 * L1 * cos(delta) * cos(delta)
    dydx[1] = (
        M2 * L1 * state[1] * state[1] * sin(delta) * cos(delta)
        + M2 * G * sin(state[2]) * cos(delta)
        + M2 * L2 * state[3] * state[3] * sin(delta)
        - (M1 + M2) * G * sin(state[0])
    ) / denominator

    dydx[2] = state[3]

    denominator *= L2 / L1
    dydx[3] = (
        -M2 * L2 * state[3] * state[3] * sin(delta) * cos(delta)
        + (M1 + M2) * G * sin(state[0]) * cos(delta)
        - (M1 + M2) * L1 * state[1] * state[1] * sin(delta)
        - (M1 + M2) * G * sin(state[2])
    ) / denominator

    return dydx


def calculate(
    theta1: float,
    omega1: float,
    theta2: float,
    omega2: float,
    time: Sequence,
) -> npt.NDArray:
    # initial state
    state = np.array([theta1, omega1, theta2, omega2]) * pi / 180.0

    # integrate your ODE using scipy.integrate.
    return integrate.odeint(derivatives, state, time)


def main():
    # create a time array from 0..100 sampled at 0.05 second steps
    dt = 0.05
    times = np.arange(0.0, 20, dt)

    # theta1 and theta2 are the initial angles (degrees)
    # omega1 and omega2 are the initial angular velocities (degrees per second)
    theta1 = 120.0
    omega1 = 0.0
    theta2 = -10.0
    omega2 = 0.0

    y = calculate(theta1, omega1, theta2, omega2, times)  # type: ignore

    x1 = L1 * sin(y[:, 0])
    y1 = -L1 * cos(y[:, 0])

    x2 = L2 * sin(y[:, 2]) + x1
    y2 = -L2 * cos(y[:, 2]) + y1

    fig = plt.figure()
    max_len = L1 + L2
    ax = fig.add_subplot(
        111,
        autoscale_on=False,
        xlim=(-max_len, max_len),
        ylim=(-max_len, max_len),
        aspect="equal",
    )
    ax.grid()

    (line,) = ax.plot([], [], "k--", lw=1)
    (line_m1,) = ax.plot([], [], "o", ms=5 * (M1 / max_len) ** 0.5)
    (line_m2,) = ax.plot([], [], "o", ms=5 * (M2 / max_len) ** 0.5)
    time_template = "time = %.1fs"
    time_text = ax.text(0.05, 0.9, "", transform=ax.transAxes)

    def init():
        line.set_data([], [])
        line_m1.set_data([], [])
        line_m2.set_data([], [])
        time_text.set_text("")
        return line, line_m1, line_m2, time_text

    def animate(i):
        thisx = [0, x1[i], x2[i]]
        thisy = [0, y1[i], y2[i]]

        line.set_data(thisx, thisy)
        line_m1.set_data([x1[i]], [y1[i]])
        line_m2.set_data([x2[i]], [y2[i]])
        time_text.set_text(time_template % (i * dt))
        return line, line_m1, line_m2, time_text

    ani = animation.FuncAnimation(  # noqa: F841
        fig, animate, np.arange(1, len(y)), interval=25, blit=True, init_func=init
    )

    # ani.save('double_pendulum.mp4', fps=15)
    plt.show()


if __name__ == "__main__":
    main()
