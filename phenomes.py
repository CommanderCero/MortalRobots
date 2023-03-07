import pygame
import math

from Box2D import b2Vec2, b2World, b2BodyDef, b2PolygonShape, b2_dynamicBody, b2CircleShape, b2FixtureDef
from pygame import Vector2

from constants import PPM

class Car:
    BODY_COLOR = pygame.Color("#238fbb")
    BODY_LINE_COLOR = pygame.Color("#1c7296")
    WHEEL_COLOR = pygame.Color("#e28743")
    WHEEL_LINE_COLOR = pygame.Color(0, 0, 0, 255)
    
    def __init__(self,
            body,
            wheels,
            wheel_motor_speed=10.0
        ):
        self.body = body
        self.wheels = wheels
        
        self.wheel_motor_speed = wheel_motor_speed
    
    def update(self):
        for wheel in self.wheels:
            wheel.joints[0].joint.motorSpeed = self.wheel_motor_speed
    
    def render(self, screen):
        self._render_body(screen)
        
    def _render_body(self, screen):
        for fixture in self.body.fixtures:
            vertices = [(self.body.transform * v) * PPM for v in fixture.shape.vertices]
            pygame.draw.polygon(screen, Car.BODY_COLOR, vertices)
            for fixture in self.body.fixtures:
                vertices = [(self.body.transform * v) * PPM for v in fixture.shape.vertices]
                for v in vertices:
                    pygame.draw.line(screen, Car.BODY_LINE_COLOR, self.body.transform.position * PPM, v, width=2)
                    
        for wheel in self.wheels:
            center = wheel.position * PPM
            radius = int(wheel.fixtures[0].shape.radius * PPM)
            dir_vec = Vector2(0, radius).rotate(math.degrees(wheel.angle))
            
            pygame.draw.circle(screen, Car.WHEEL_COLOR, center, radius)
            pygame.draw.line(screen, Car.WHEEL_LINE_COLOR, center, center + dir_vec, width=2)
        
    @property
    def position(self):
        return Vector2(self.body.position)
    
    @staticmethod
    def create_test_car(world: b2World, position):
        body = world.CreateDynamicBody(position=position)
        body.CreatePolygonFixture(box=(2,1), density=1, friction=0.3)
        
        return Car(body, [])