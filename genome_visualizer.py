from game_base import GameBase
from genomes import CarGenome
from Box2D import b2World, b2PolygonShape
from constants import PPM
from pygame import Vector2

import pygame

class GenomeVisualizer(GameBase):
    def __init__(self, screen_width, screen_height):
        super().__init__("Genome Visualizer", screen_width, screen_height)
        
        self.genome_left = CarGenome(body_vertices=10)
        self.genome_right = CarGenome(body_vertices=10)
        
        self.init()
        self.move_camera((-screen_width//2,0))
        
    def init(self):
        self.world = b2World(gravity=(0,9.87))
        self.car_left = self.genome_left.create_car(self.world, (-10, 19))
        self.car_right = self.genome_right.create_car(self.world, (10, 19))
        self.floor = self.world.CreateStaticBody(
            position=(0, 24),
            shapes=b2PolygonShape(box=(100, 1)),
        )
        
    def fixed_step(self, delta_time):
        self.world.Step(2./60,10,10)
    
    def render(self):
        ground_shape = self.floor.fixtures[0].shape
        vertices = [(self.floor.transform * v) * PPM for v in ground_shape.vertices]
        self.draw_polygon(pygame.Color("GRAY"), vertices)
        
        self.car_left.render(self)
        self.car_right.render(self)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.genome_left.mutate(0.1)
                self.init()
            if event.key == pygame.K_RIGHT:
                self.genome_right.mutate(0.1)
                self.init()
    
if __name__ == "__main__":
    renderer = GenomeVisualizer(800, 600)
    renderer.run()