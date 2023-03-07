import numpy as np
import math

from Box2D import (
    b2Vec2, b2World, b2BodyDef, b2CircleShape,
    b2FixtureDef, b2PolygonShape, b2_dynamicBody
)
from pygame import Vector2

from phenomes import Car

class CarGenome:
    def __init__(self, body_vertices=10):
        self.magnitudes = np.random.uniform(0.1, 4, size=body_vertices)
        self.angles = np.random.uniform(0, 1, size=body_vertices)
        self.wheels_flags = np.random.randint(0, 2, size=body_vertices, dtype=bool)
        self.wheel_size = np.random.uniform(0.1, 1, size=body_vertices)
        self.wheel_motor_speed = 10.0
        self.fitness = 0

    def mutate(self):
        mutation_rate = 0.1
        mag_indices = np.where(np.random.uniform(0, 1, size=len(self.magnitudes)) < mutation_rate)
        angle_indices = np.where(np.random.uniform(0, 1, size=len(self.angles)) < mutation_rate)
        wheel_indices = np.where(np.random.uniform(0, 1, size=len(self.wheels_flags)) < mutation_rate)
        indices = np.where(np.random.uniform(0, 1, size=len(self.wheel_size)) < mutation_rate)

        self.magnitudes[mag_indices] = np.random.uniform(0.1, 4, size=len(self.magnitudes[mag_indices]))
        self.angles[angle_indices] = np.random.uniform(0, 1, size=len(self.angles[angle_indices]))
        self.wheels_flags[wheel_indices] = np.random.randint(0, 2, size=len(self.wheels_flags[wheel_indices]))
        self.wheel_size[indices] = np.random.randint(0.1, 1.5, size=len(self.wheel_size[indices]))

    def crossover(self, other: "CarGenome"):
        #t = np.random.uniform(0, 1)
        t = np.random.uniform(0, 1, size=len(self.magnitudes))
        new_magnitudes = t * self.magnitudes + (1 - t) * other.magnitudes
        new_angles = t * self.angles + (1 - t) * other.angles
        new_size = t * self.wheel_size + (1 - t) * other.wheel_size

        self.magnitudes = (1 - t) * self.magnitudes + t * other.magnitudes
        self.angles = (1 - t) * self.angles + t * other.angles
        self.wheel_size = (1 - t) * self.wheel_size + t * other.wheel_size
        other.magnitudes = new_magnitudes
        other.angles = new_angles
        other.wheel_size = new_size

    def create_car(self, world: b2World, position, is_flipped=False):
        vertices = []
        total_angle_sum = sum(self.angles)
        running_angle_sum = 0
        for m, a in zip(self.magnitudes, self.angles):
            running_angle_sum += a

            vec = Vector2(1, 0)
            vec = vec.rotate((running_angle_sum / total_angle_sum) * 360)
            vec *= m
            vertices.append(tuple(vec))

        wheel_speed = self.wheel_motor_speed
        if is_flipped:
            vertices = [(-x, y) for x, y in vertices]
            wheel_speed = -wheel_speed

        car = world.CreateDynamicBody(position=position)
        body_parts = []
        for i in range(len(vertices)):
            triangle = [vertices[i], vertices[(i+1) % len(vertices)], (0, 0)]
            body_parts.append(car.CreatePolygonFixture(vertices=triangle, density=1))
        wheels, wheels_bodies = self._create_wheels_bodies(world, car, vertices)
        return Car(car, wheels_bodies, wheel_motor_speed=wheel_speed)

    def create_body(self, world: b2World, position):
        vertices = []
        total_angle_sum = sum(self.angles)
        running_angle_sum = 0
        for m, a in zip(self.magnitudes, self.angles):
            running_angle_sum += a

            vec = Vector2(1, 0)
            vec = vec.rotate((running_angle_sum / total_angle_sum) * 360)
            vec *= m
            vertices.append(tuple(vec))

        body = world.CreateDynamicBody(position=position)
        for i in range(len(vertices)):
            self._create_body_part(body, vertices[i], vertices[(i+1) % len(vertices)], density=1)
        self.wheels, wheels_bodies = self._create_wheels_bodies(world, body, vertices)

        return body, wheels_bodies

    def _create_body_part(self, body, v1, v2, density):
        vertices = [v1, v2, (0, 0)]
        body.CreatePolygonFixture(vertices=vertices, density=density)

    def _create_wheels_bodies(self, world, body, vertices):
        wheels = []
        wheels_bodies = []
        for wheel_ind, is_wheel in enumerate(self.wheels_flags):
            if not is_wheel:
                continue

            vertex = vertices[wheel_ind]
            angle = 0  # np.random.uniform(0, 2 * math.pi)
            wheel_body = world.CreateDynamicBody(
                position=body.worldCenter + b2Vec2(vertex[0], vertex[1]),
                # angle=angle
            )
            wheel_shape = b2CircleShape(radius=self.wheel_size[wheel_ind])
            wheel_fixture = b2FixtureDef(shape=wheel_shape, density=5.0, friction=1)
            wheel_body.CreateFixture(wheel_fixture)
            wheel_joint = world.CreateRevoluteJoint(
                bodyA=body,
                bodyB=wheel_body,
                # anchor=wheel_body.position,
                localAnchorA=b2Vec2(vertex[0], vertex[1]),
                localAnchorB=(0, 0),
                collideConnected=False,
                enableMotor=True,
                maxMotorTorque=100,
                motorSpeed=0,
            )
            wheels_bodies.append(wheel_body)
            wheels.append((wheel_body, wheel_joint))

        return wheels, wheels_bodies

    def update(self):
        for wheel in self.wheels:
            if wheel is not None:
                wheel[1].motorSpeed = self.wheel_motor_speed
