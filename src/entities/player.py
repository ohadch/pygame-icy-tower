import copy

import pygame
from pygame.color import THECOLORS

from src.dimensions.position import Position
from src.dimensions.vector import Vector
from src.entities.entity import Entity


class PlayerEntity(Entity):

    def __init__(self, window):
        self.window = window
        self.radius_m = 1
        self.padding_m = 1.0
        self.position = Position(self.window.env.width_m / 2, self.window.env.height_m - self.radius_m)
        self.vector = Vector(0, 0)
        self.jump_mps = 70
        self.speed_mps = 70
        self.is_jumping = False
        self.step = None
        self.previous_vector = Vector(0, 0)
        self.in_combo = False
        self.time_moving_to_side = 0.0
        self.time_since_last_side_movement = 0.0

    def top_vertex(self):
        return Position(self.position.x_m, self.position.y_m - self.radius_m)

    def bottom_vertex(self):
        return Position(self.position.x_m, self.position.y_m + self.radius_m)

    def left_vertex(self):
        return Position(self.position.x_m - self.radius_m, self.position.y_m)

    def right_vertex(self):
        return Position(self.position.x_m + self.radius_m, self.position.y_m)

    def is_penetrating_floor(self):
        return (self.bottom_vertex().y_m - self.window.env.height_m) > 0

    def floor_penetration(self):
        return self.bottom_vertex().y_m - self.window.env.height_m

    def fix_sticky_bottom(self):
        self.position.y_m += (self.window.env.height_m - self.bottom_vertex().y_m)
        if self.vector.y_mps > 0:
            self.vector.y_mps = 0

    def move_right(self):
        if self.right_vertex().x_m <= self.window.env.width_m:
            self.position.x_m += self.speed_mps * self.window.session.dt_s

    def move_left(self):
        if self.left_vertex().x_m > 0:
            self.position.x_m -= self.speed_mps * self.window.session.dt_s

    def get_jump_rate_mps(self):
        combo_jump = self.jump_mps * 3
        if self.time_moving_to_side > 0.5:
            if not self.in_combo:
                self.in_combo = True
            jump = combo_jump
        elif 0.0 < self.time_moving_to_side < 0.5:
            if self.in_combo:
                jump = combo_jump
            jump = self.jump_mps * 1.5
        else:
            jump = self.jump_mps
            self.in_combo = False
        return jump

    def apply_gravity(self):
        self.vector.y_mps += self.window.env.gravity_mps2 * self.window.session.dt_s

    def is_on_step(self, step):
        return self.vector.y_mps >= 0 and float(step.left_edge().x_m) < self.position.x_m < float(step.right_edge().x_m) and abs(self.bottom_vertex().y_m - step.center_m.y_m) <= self.padding_m

    def stand_on_step(self, step):
        self.step = step
        self.position.y_m = self.step.center_m.y_m - self.radius_m
        self.vector.y_mps = self.step.vector.y_mps
        self.is_jumping = False
        self.window.session.score = step.id

    def update(self):
        self.apply_gravity()

        if self.time_since_last_side_movement < 0.2:
            self.time_moving_to_side += self.time_since_last_side_movement

        if self.is_jumping:
            if self.previous_vector.y_mps == 0:
                self.vector.y_mps -= self.get_jump_rate_mps()
                self.position.y_m -= self.padding_m * 1.5
            elif self.previous_vector.y_mps > 0:
                for step in self.window.air_track.steps:
                    if self.is_on_step(step):
                        self.stand_on_step(step)
        else:
            for step in self.window.air_track.steps:
                if self.is_on_step(step):
                    self.stand_on_step(step)

        self.position.y_m += self.vector.y_mps * self.window.session.dt_s
        self.previous_vector = copy.deepcopy(self.vector)

    def draw(self):
        pygame.draw.circle(self.window.surface, THECOLORS['blue'], self.position.coordinates_px(self.window.env.m_to_px_ratio), self.window.env.m_to_px(self.radius_m))
