from Box2D import b2Vec2, b2World, b2BodyDef, b2PolygonShape, b2_dynamicBody
import pygame

from constants import PPM

class Creature:
    BODY_COLOR = pygame.Color("#238fbb")
    BODY_LINE_COLOR = pygame.Color("#1c7296")
    
    def __init__(self, body, weapon, wheels):
        self.body = body
        self.weapon = weapon
        self.wheels = wheels
    
    def update(self):
        pass
    
    def render(self, screen):
        self._render_body(screen)
        
    def _render_body(self, screen):
        for fixture in self.body.fixtures:
            vertices = [(self.body.transform * v) * PPM for v in fixture.shape.vertices]
            pygame.draw.polygon(screen, Creature.BODY_COLOR, vertices, width=2)
            for fixture in self.body.fixtures:
                vertices = [(self.body.transform * v) * PPM for v in fixture.shape.vertices]
                for v in vertices:
                    pygame.draw.line(screen, Creature.BODY_LINE_COLOR, self.body.transform.position * PPM, v, width=2)
    
    @staticmethod
    def create_test_creature(world: b2World, position):
        body = world.CreateDynamicBody(position=position)
        body.CreatePolygonFixture(box=(2,1), density=1, friction=0.3)
        
        return Creature(body, None, [])