import numpy as np
import math

from Box2D import (
    b2Vec2, b2World, b2BodyDef, b2CircleShape,
    b2FixtureDef, b2PolygonShape, b2_dynamicBody
)
from pygame import Vector2


class TestGenome:
    def __init__(self, body_vertices=10):
        self.magnitudes = np.random.uniform(0.1, 4, size=body_vertices)
        self.angles = np.random.uniform(0, 1, size=body_vertices)
        self.wheels_flags = np.random.randint(0, 2, size=body_vertices)
        self.fitness = 0
    
    def mutate(self):
        mutation_rate = 0.1
        mag_indices = np.where(np.random.uniform(0, 1, size=len(self.magnitudes)) < mutation_rate)
        angle_indices = np.where(np.random.uniform(0, 1, size=len(self.angles)) < mutation_rate)
        
        self.magnitudes[mag_indices] = np.random.uniform(0.1, 4, size=len(self.magnitudes[mag_indices]))
        self.angles[angle_indices] = np.random.uniform(0, 1, size=len(self.angles[angle_indices]))
    
    def crossover(self, other: "TestGenome"):
        #t = np.random.uniform(0, 1)
        t = np.random.uniform(0, 1, size=len(self.magnitudes))
        new_magnitudes = t * self.magnitudes + (1 - t) * other.magnitudes
        new_angles = t * self.angles + (1 - t) * other.angles
        
        self.magnitudes = (1 - t) * self.magnitudes + t * other.magnitudes
        self.angles = (1 - t) * self.angles + t * other.angles
        other.magnitudes = new_magnitudes
        other.angles = new_angles

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

        self.wheels = []
        wheels_bodies = []
        for wheel_ind, is_wheel in enumerate(self.wheels_flags):
            if is_wheel == 0:
                continue

            vertex = vertices[wheel_ind]
            angle = 0  # np.random.uniform(0, 2 * math.pi)
            wheel_body = world.CreateDynamicBody(
                position=body.worldCenter + b2Vec2(vertex[0], vertex[1]),
                # angle=angle
            )
            wheel_shape = b2CircleShape(radius=0.5)
            wheel_fixture = b2FixtureDef(shape=wheel_shape, density=1.0)
            wheel_body.CreateFixture(wheel_fixture)
            wheel_joint = world.CreateRevoluteJoint(
                bodyA=body,
                bodyB=wheel_body,
                anchor=wheel_body.position,
                collideConnected=False,
                enableMotor=True,
                maxMotorTorque=100,
                motorSpeed=0,
            )
            wheels_bodies.append(wheel_body)
            self.wheels.append((wheel_body, wheel_joint))

        return body, wheels_bodies

    def _create_body_part(self, body, v1, v2, density):
        vertices = [v1, v2, (0, 0)]
        body.CreatePolygonFixture(vertices=vertices, density=density)

    def update(self):
        for wheel in self.wheels:
            if wheel is not None:
                wheel[1].motorSpeed = 10
