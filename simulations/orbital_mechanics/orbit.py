from dataclasses import dataclass

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


@dataclass
class Coordinates:
    x: float
    y: float


@dataclass
class CoordinatesHistory:
    x: list[float]
    y: list[float]


class Orbit:
    GM = 1.0  # graviational constant times mass of the star

    def __init__(
        self,
        initial_position: Coordinates = Coordinates(1, 0),
        initial_velocity: Coordinates = Coordinates(0, 1),
        time_step=0.1,
    ):
        self.position: Coordinates = initial_position
        self.velocity: Coordinates = initial_velocity
        self.time_step = time_step

        self.position_history: CoordinatesHistory = CoordinatesHistory(
            x=[initial_position.x],
            y=[initial_position.y],
        )

    @staticmethod
    def get_acceleration_gravity(position: Coordinates) -> Coordinates:
        acceleration = -Orbit.GM / (position.x**2.0 + position.y**2.0) ** 1.5
        return Coordinates(
            acceleration * position.x,
            acceleration * position.y,
        )

    def update_orbit(self):
        acceleration = self.get_acceleration_gravity(self.position)

        self.velocity.x += acceleration.x * self.time_step
        self.velocity.y += acceleration.y * self.time_step

        self.position.x += self.velocity.x * self.time_step
        self.position.y += self.velocity.y * self.time_step

        self.position_history.x.append(self.position.x)
        self.position_history.y.append(self.position.y)


class OrbitAnimation(Orbit):
    def __init__(
        self,
        initial_position: Coordinates = Coordinates(1, 0),
        initial_velocity: Coordinates = Coordinates(0, 1),
        time_step=0.1,
    ):
        super().__init__(
            initial_position,
            initial_velocity,
            time_step,
        )

        self.star: Line2D
        self.planet: Line2D
        self.orbit: Line2D

    def animate(self, *args):
        self.update_orbit()

        # Update orbit. Plot only last 1000 points
        self.orbit.set_data(
            self.position_history.x[-1000:],
            self.position_history.y[-1000:],
        )
        # Update planet position
        self.planet.set_data(
            self.position_history.x[-1:],
            self.position_history.y[-1:],
        )

        self.axis.relim()
        self.axis.autoscale_view()

    def run_animation(self):
        self.fig, self.axis = plt.subplots()
        self.axis.set_aspect("equal")

        # Star is at coordinates (0, 0)
        (self.star,) = self.axis.plot(
            [0],
            [0],
            "yo",
            ms=10,
        )

        # Orbit
        (self.orbit,) = self.axis.plot(
            self.position_history.x,
            self.position_history.y,
        )

        # Planet
        (self.planet,) = self.axis.plot(
            self.position.x,
            self.position.y,
            "ro",
        )

        return animation.FuncAnimation(
            self.fig,
            self.animate,  # type: ignore
            interval=25,
            blit=False,
        )


if __name__ == "__main__":
    orbit_anim = OrbitAnimation(
        initial_velocity=Coordinates(x=0, y=0.5),
        time_step=0.005,
    )

    ani = orbit_anim.run_animation()
    plt.show()
