import pygame
import random
from pygame.color import THECOLORS


# ==================
# Infrastructure Classes
# ==================

class Session:

    def __init__(self):
        self.dt_s = None
        self.time_sec = 0.0

    def advance_time(self):
        self.time_sec += self.dt_s


class GameWindow:

    def __init__(self, environment):

        self.session = Session()
        self.env = environment
        self.air_track = AirTrack(self)

        pygame.init()

        self.dimensions_px = self.env.dimensions_px
        self.surface = pygame.display.set_mode(self.dimensions_px)
        self.erase_and_update()

        self.frame_rate_limit = 100
        self.clock = pygame.time.Clock()

        self.done = False

    def erase_and_update(self):
        self.surface.fill(THECOLORS['black'])
        pygame.display.flip()

    def get_user_input(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_RIGHT]:
            self.air_track.player.move_right()
        elif pressed_keys[pygame.K_LEFT]:
            self.air_track.player.move_left()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.air_track.player.is_jumping:
                        self.air_track.player.jump()

    def loop(self):
        while not self.done:
            self.surface.fill(THECOLORS['black'])

            # Get the delta t for one frame rate (this changes depending on system load)
            self.session.dt_s = float(self.clock.tick(self.frame_rate_limit) * 1e-3)

            self.get_user_input()
            self.air_track.player.update()
            game_window.air_track.player.draw()

            for step in self.air_track.steps:
                step.draw()

            self.session.advance_time()

            pygame.display.flip()


# ==================
# Dimensional Classes
# ==================


class Position:

    def __init__(self, x_m, y_m):
        self.x_m = x_m
        self.y_m = y_m

    def coordinates_m(self):
        return self.x_m, self.y_m

    def coordinates_px(self, m_to_px_ratio):
        return int(self.x_m * m_to_px_ratio), int(self.y_m * m_to_px_ratio)


class Vector:

    def __init__(self, x_mps, y_mps):
        self.x_mps = x_mps
        self.y_mps = y_mps


class Environment:

    def __init__(self, width_m, height_m, width_px):
        self.gravity_mps2 = 50
        self.dimensions_m = self.width_m, self.height_m = width_m, height_m
        self.m_to_px_ratio = width_px / self.width_m
        self.dimensions_px = self.width_px, self.height_px = width_px, self.m_to_px(self.height_m)

    def m_to_px(self, m):
        return int(m * self.m_to_px_ratio)


class AirTrack:

    def __init__(self, window):
        self.window = window
        self.player = Player(self.window)
        self.steps_num = 5
        self.steps = []
        self.draw_steps()

    def draw_steps(self):
        margins_m = self.window.env.height_m / self.steps_num
        y_positions_m = range(margins_m, self.window.env.height_m, margins_m)
        for y_pos_m in y_positions_m:
            s = Step(self.window)
            s.center_m.y_m = y_pos_m
            self.steps.append(s)

# ==================
# Object Classes
# ==================


class Step:

    def __init__(self, window):
        self.window = window
        self.min_length_m = 10
        self.max_length_m = 20
        self.length_m = random.randint(self.min_length_m, self.max_length_m)
        self.center_m = self.rand_pos()
        self.color = THECOLORS['greenyellow']
        self.vector = Vector(0, 0)

    def right_edge(self):
        return Position(self.center_m.x_m + int(self.length_m / 2), self.center_m.y_m)

    def left_edge(self):
        return Position(self.center_m.x_m - int(self.length_m / 2), self.center_m.y_m)

    def rand_pos(self):
        x_m = random.randint(0, self.window.env.width_m - self.length_m)
        return Position(x_m, self.window.env.height_m - 10)

    def draw(self):
        pygame.draw.line(self.window.surface, self.color, self.left_edge().coordinates_px(self.window.env.m_to_px_ratio), self.right_edge().coordinates_px(self.window.env.m_to_px_ratio), 3)


class Player:

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

    def jump(self):
        self.is_jumping = True
        self.vector.y_mps -= self.jump_mps
        self.step = None

    def apply_gravity(self):
        self.vector.y_mps += self.window.env.gravity_mps2 * self.window.session.dt_s

    def is_colliding(self):
        return self.is_penetrating_floor()

    def is_on_step(self, step):
        return self.vector.y_mps >= 0 and float(step.left_edge().x_m) < self.position.x_m < float(step.right_edge().x_m) and abs(self.bottom_vertex().y_m - step.center_m.y_m) <= self.padding_m

    def stand_on_step(self, step):
        self.step = step
        self.position.y_m = self.step.center_m.y_m - self.radius_m
        self.vector.y_mps = self.step.vector.y_mps

    def update(self):
        self.apply_gravity()

        if self.is_jumping:
            self.apply_gravity()
            if self.is_colliding() and not self.vector.y_mps < 0:
                self.vector.y_mps = 0
                self.is_jumping = False
        else:
            if self.is_penetrating_floor():
                self.fix_sticky_bottom()

        for step in self.window.air_track.steps:
            if self.is_on_step(step):
                self.stand_on_step(step)

        self.position.y_m += self.vector.y_mps * self.window.session.dt_s

    def draw(self):
        pygame.draw.circle(self.window.surface, THECOLORS['blue'], self.position.coordinates_px(self.window.env.m_to_px_ratio), self.window.env.m_to_px(self.radius_m))


# ==================
# Main
# ==================


if __name__ == '__main__':
    e = Environment(70, 50, 1000)
    game_window = GameWindow(e)
    game_window.loop()
