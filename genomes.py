import numpy as np
import math

from Box2D import b2Vec2, b2World, b2BodyDef, b2PolygonShape, b2_dynamicBody
from pygame import Vector2

class TestGenome:
    def __init__(self, body_vertices=10):
        self.magnitudes = np.random.uniform(0.1, 4, size=body_vertices)
        self.angles = np.random.uniform(0, 2 * math.pi, size=body_vertices)
    
    def create_body(self, world: b2World, position):
        vertices = []
        for m, a in zip(self.magnitudes, self.angles):
            vec = Vector2(1, 0)
            vec = vec.rotate(math.degrees(a))
            vec *= m
            vertices.append(tuple(vec))
        
        body = world.CreateDynamicBody(position=position)
        box = body.CreatePolygonFixture(vertices=vertices, density=1, friction=0.3)
        return body