import math
import pygame

from Box2D import b2Vec2, b2World, b2BodyDef, b2PolygonShape, b2_dynamicBody, b2CircleShape, b2FixtureDef
from pygame import Vector2
from game_base import GameBase

from constants import PPM

class Car:
    # BODY_COLOR = pygame.Color("#238fbb")
    # BODY_COLOR = pygame.Color(30, 30, 255, 255)
    BODY_LINE_COLOR = pygame.Color("#1c7296")
    # WHEEL_COLOR = pygame.Color("#e28743")
    WHEEL_LINE_COLOR = pygame.Color(0, 0, 0, 255)
    
    def __init__(
            self,
            body,
            wheels,
            wheel_motor_speed,
            body_density,
            wheel_density,
        ):
        self.body = body
        self.wheels = wheels
        self.wheel_motor_speed = wheel_motor_speed
        self.body_density = body_density
        self.wheel_density = wheel_density
    
    def update(self):
        for wheel in self.wheels:
            wheel.joints[0].joint.motorSpeed = self.wheel_motor_speed
    
    def render(self, game: GameBase):
        self._render_body(game)
        self._render_wheels(game)
        
    def _render_body(self, game: GameBase):
        for fixture in self.body.fixtures:
            vertices = [(self.body.transform * v) * PPM for v in fixture.shape.vertices]
            body_color = pygame.Color(30, 30, 230 - int(self.body_density * 200), 255)
            game.draw_polygon(body_color, vertices)
            for fixture in self.body.fixtures:
                vertices = [(self.body.transform * v) * PPM for v in fixture.shape.vertices]
                for v in vertices:
                    game.draw_line(Car.BODY_LINE_COLOR, self.body.transform.position * PPM, v, width=2)
                    
    def _render_wheels(self, game: GameBase):
        for wheel in self.wheels:
            center = wheel.position * PPM
            radius = int(wheel.fixtures[0].shape.radius * PPM)
            dir_vec = Vector2(0, radius).rotate(math.degrees(wheel.angle))
            
            wheel_color = pygame.Color(255 - int(self.wheel_density * 200),
                                       255 - int(self.wheel_density * 200),
                                       0, 255)
            game.draw_circle(wheel_color, center, radius)
            game.draw_line(Car.WHEEL_LINE_COLOR, center, center + dir_vec, width=2)
        
    @property
    def position(self):
        return Vector2(self.body.position)
    
    @staticmethod
    def create_test_car(world: b2World, position):
        body = world.CreateDynamicBody(position=position)
        body.CreatePolygonFixture(box=(2,1), density=1, friction=0.3)
        
        return Car(body, [])