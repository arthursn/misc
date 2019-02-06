import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class OrbitAnimation():
    def __init__(self, x=1, y=0, vx=0, vy=1, dt=.1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.dt = dt

        self.x_orbit = [self.x]
        self.y_orbit = [self.y]

    def acceleration(self, x, y):
        GM = 1.  # graviational constant times mass of the star
        a = -GM/(x**2. + y**2.)**1.5
        return a*x, a*y

    def animate(self, *args):
        ax, ay = self.acceleration(self.x, self.y)

        self.vx += ax*self.dt
        self.vy += ay*self.dt

        self.x += self.vx*self.dt
        self.y += self.vy*self.dt

        self.x_orbit.append(self.x)
        self.y_orbit.append(self.y)

        # Update orbit. Plot only last 1000 points
        self.orbit.set_data(self.x_orbit[-1000:], self.y_orbit[-1000:])
        # Update planet position
        self.planet.set_data(self.x_orbit[-1], self.y_orbit[-1])

        self.axis.relim()
        self.axis.autoscale_view()

    def run_animation(self):
        self.fig, self.axis = plt.subplots()
        self.axis.set_aspect('equal')

        # Star is at coordinates (0, 0)
        self.star, = self.axis.plot([0], [0], 'yo', ms=10)

        # Orbit
        self.orbit, = self.axis.plot(self.x_orbit, self.y_orbit)

        # Planet
        self.planet, = self.axis.plot(self.x_orbit[-1], self.y_orbit[-1], 'ro')

        return animation.FuncAnimation(self.fig, self.animate,
                                       interval=25, blit=False)


if __name__ == '__main__':
    orbit = OrbitAnimation(vy=.5, dt=.005)

    ani = orbit.run_animation()
    plt.show()
