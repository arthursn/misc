from itertools import cycle

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


class CelestialBody:
    def __init__(self, mass, position, velocity, history=False):
        self.mass = mass
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.history = history
        if self.history:
            self._position_history_list = [position]
            self._position_history = np.array(self._position_history_list).T

    @property
    def position_history(self):
        if self._position_history.shape[1] != len(self._position_history_list):
            self._position_history = np.array(self._position_history_list).T
        return self._position_history

    def update_position(self, position):
        self.position = position
        if self.history:
            self._position_history_list.append(position)

    def update_velocity(self, velocity):
        self.velocity = velocity


class PlanetarySystem:
    G = 1.0  # gravitational constant

    def __init__(self):
        # pass
        self.list_bodies = []
        self.nbodies = 0
        self.matrix_forces = np.zeros((0, 0, 2))
        self.list_forces = np.zeros((0, 2))

    def add_body(self, body):
        if isinstance(body, CelestialBody):
            self.list_bodies.append(body)
            self.nbodies += 1
            self.matrix_forces = np.zeros((self.nbodies, self.nbodies, 2))
            self.list_forces = np.zeros((self.nbodies, 2))

            # Return index of body in self.list_bodies
            return self.nbodies - 1
        else:
            print("{} is not a CelestialBody object".format(body))

    def get_force_two_bodies(self, body1, body2):
        r = body1.position - body2.position
        return self.G * body1.mass * body2.mass * r / np.linalg.norm(r) ** 3.0

    def get_forces_all_bodies(self):
        for i in range(0, self.nbodies - 1):
            for j in range(i + 1, self.nbodies):
                self.matrix_forces[i, j] = self.get_force_two_bodies(
                    self.list_bodies[i], self.list_bodies[j]
                )
                self.matrix_forces[j, i] = -self.matrix_forces[i, j]

        self.list_forces[:, :] = self.matrix_forces.sum(axis=0)

    def calculate_dynamics(self, dt):
        self.get_forces_all_bodies()

        for i in range(self.nbodies):
            acceleration = self.list_forces[i] / self.list_bodies[i].mass
            velocity = self.list_bodies[i].velocity + acceleration * dt
            position = self.list_bodies[i].position + velocity * dt

            self.list_bodies[i].update_position(position)
            self.list_bodies[i].update_velocity(velocity)


if __name__ == "__main__":
    niterations = 4000
    dt = 0.1
    plot_last = 200

    sun = CelestialBody(1e0, [0, 0], [0, 0], True)
    GM_root = (PlanetarySystem.G * sun.mass) ** 0.5

    # Set initial velocity that leads to an approximate circular orbit
    # mercury = CelestialBody(5e-3, [0.4, 0], [0, .9*GM_root/0.4**.5], True)
    # venus = CelestialBody(1e-4, [0.7, 0], [0, GM_root/0.7**.5], True)
    earth = CelestialBody(1e-4, [1.0, 0], [0, GM_root / 1.0**0.5], True)
    mars = CelestialBody(5e-2, [-1.5, 0], [0, -1.03 * GM_root / 1.5**0.5], True)
    ceres = CelestialBody(5e-2, [0, -3.0], [-0.98 * GM_root / 3.0**0.5, 0], True)
    jupiter = CelestialBody(1e-1, [0, 5.0], [1.05 * GM_root / 5.0**0.5, 0], True)

    solar_system = PlanetarySystem()
    solar_system.add_body(sun)
    # solar_system.add_body(mercury)
    # solar_system.add_body(venus)
    solar_system.add_body(earth)
    solar_system.add_body(mars)
    solar_system.add_body(ceres)
    solar_system.add_body(jupiter)

    # iterations
    for it in range(niterations):
        solar_system.calculate_dynamics(dt)

    cycolors = cycle(["y", "b", "r", "0.5", "m"])
    cysizes = cycle([4, 2, 2, 2, 2])

    # Setup animation
    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)

    orbits = []
    current_positions = []
    for body in solar_system.list_bodies:
        color = next(cycolors)
        orbits += ax.plot(*body.position_history[:, :0], c=color, ls="-")
        current_positions += ax.plot(
            *body.position_history[:, 0],
            c=color,
            ls="none",
            marker="o",
            ms=next(cysizes),
        )

    def init():
        for orbit, position in zip(orbits, current_positions):
            orbit.set_data([], [])
            position.set_data([], [])
        return orbits + current_positions

    first_point = np.arange(niterations) - plot_last
    first_point[first_point < 0] = 0

    def animate(it):
        for idx, body in enumerate(solar_system.list_bodies):
            orbits[idx].set_data(*body.position_history[:, first_point[it] : it])
            current_positions[idx].set_data(*body.position_history[:, it : it + 1])
        return orbits + current_positions

    ani = animation.FuncAnimation(
        fig=fig,
        func=animate,
        frames=range(niterations),
        interval=10,
        blit=True,
        init_func=init,
    )

    # ani.save('orbits.gif', writer='pillow')

    plt.show()
