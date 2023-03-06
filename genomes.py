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
        for m, a in sorted(zip(self.magnitudes, self.angles), key=lambda x: x[1]):
            vec = Vector2(1, 0)
            vec = vec.rotate(math.degrees(a))
            vec *= m
            vertices.append(tuple(vec))
        
        
        body = world.CreateDynamicBody(position=position)
        for i in range(len(vertices)):
            self._create_body_part(body, vertices[i], vertices[(i+1) % len(vertices)], density=1)
        #for v1, v2 in zip(vertices[:-1], vertices[1:]):
        #    self._create_body_part(body, v1, v2, density=1)
        return body
    
    def _create_body_part(self, body, v1, v2, density):
        vertices = [v1, v2, (0, 0)]
        body.CreatePolygonFixture(vertices=vertices, density=density)