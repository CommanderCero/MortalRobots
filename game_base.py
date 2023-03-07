import pygame
from pygame import Vector2

from abc import ABC, abstractmethod

class GameBase(ABC):
    def __init__(self, title, screen_width, screen_height, fps=60):
        pygame.init()
        
        self.fps = fps
        self.fixed_delta_time = 1. / self.fps
        self.clock = pygame.time.Clock()
        self.background_color = pygame.Color("white")
        
        self.camera_pos = Vector2(0,0)
        
        self.screen = pygame.display.set_mode((screen_width, screen_width), 0, 32)
        pygame.display.set_caption(title)
        
    def run(self):
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # The user closed the window or pressed escape
                    running = False
                else:
                    self.handle_event(event)
            
            # Simulate
            self.fixed_step(self.fixed_delta_time)
            # Render
            self.screen.fill(self.background_color)
            self.render()
            # Display newly rendered frame
            pygame.display.flip()
            # Wait to render the next frame
            self.clock.tick(self.fps)
        pygame.quit()
    
    def draw_line(self, color, start_pos, end_pos, width=0):
        pygame.draw.line(self.screen, color, start_pos - self.camera_pos, end_pos - self.camera_pos, width)
        
    def draw_circle(self, color, center, radius, width=0):
        pygame.draw.circle(self.screen, color, center - self.camera_pos, radius, width)
        
    def draw_polygon(self, color, points, width=0):
        pygame.draw.polygon(self.screen, color, [p - self.camera_pos for p in points], width)
        
    def move_camera(self, delta):
        self.camera_pos += delta
    
    @abstractmethod
    def fixed_step(self, delta_time):
        pass
    
    @abstractmethod
    def render(self):
        pass
    
    @abstractmethod
    def handle_event(self, event):
        pass