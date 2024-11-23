import random

import pygame
from pygame.color import THECOLORS

from src.dimensions.position import Position
from src.dimensions.vector import Vector
from src.entities.entity import Entity


class StepEntity(Entity):

    def __init__(self, window, id_):
        self.window = window
        self.min_length_m = 25
        self.max_length_m = 35
        self.length_m = random.randint(self.min_length_m, self.max_length_m)
        self.center_m = self.rand_pos()
        self.color = self.window.step_color
        self.vector = Vector(0, 0)
        self.id = id_
        self.should_draw_score = False

    def right_edge(self):
        return Position(self.center_m.x_m + int(self.length_m / 2), self.center_m.y_m)

    def left_edge(self):
        return Position(self.center_m.x_m - int(self.length_m / 2), self.center_m.y_m)

    def rand_pos(self):
        x_m = random.randint(0, self.window.env.width_m - self.length_m)
        return Position(x_m, self.window.env.height_m - 10)

    def draw_score(self):
        w = 6
        h = 2
        rect = pygame.Rect(self.window.env.m_to_px(self.center_m.x_m - w / 3), self.window.env.m_to_px(self.center_m.y_m), self.window.env.m_to_px(w), self.window.env.m_to_px(h))
        pygame.draw.rect(self.window.surface, self.color, rect)
        floor_num = self.window.hud_font.render(str(self.id), 5, THECOLORS['black'])
        w, h = self.center_m.coordinates_px(self.window.env.m_to_px_ratio)
        self.window.surface.blit(floor_num, (w, h))

    def draw(self):
        pygame.draw.line(self.window.surface, self.color, self.left_edge().coordinates_px(self.window.env.m_to_px_ratio), self.right_edge().coordinates_px(self.window.env.m_to_px_ratio), 3)
        if self.should_draw_score:
            self.draw_score()
