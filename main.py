"""
Things I have learnt:
1. Never underestimate the difference between int and float.


TODO:
[] Combos

[V] Show HUD
[V] As game advances, accelerate scrolling rate
[V] Control jump height by x axis speed / combo
[V] Always keep player at the middle of the screen
"""


import pygame
import random
import copy
from pygame.color import THECOLORS


# ==================
# Infrastructure Classes
# ==================


class Session:

    def __init__(self):
        """
        The session objects controls the time in the game.
        """
        self.dt_s = None
        self.time_sec = 0.0
        self.score = 0

    def advance_time(self):
        self.time_sec += self.dt_s


class GameWindow:

    def __init__(self, environment):
        """
        Controls the UI, in this case Pygame window.
        :param environment: Environment object.
        """

        # Colors
        self.background_color = THECOLORS['black']
        self.curr_color_name = random.choice(THECOLORS.keys())
        self.step_color = THECOLORS[self.curr_color_name]

        # Creates a composition of session, environment, game window and air track.
        self.session = Session()
        self.env = environment
        self.air_track = AirTrack(self)

        # Initializing Pygame.
        pygame.init()

        # Fonts
        self.hud_font = pygame.font.SysFont("monospace", 30)

        # Gets screen dimensions in pixels from the environment object and sets the surface attribute.
        self.dimensions_px = self.width_px, self.height_px = self.env.dimensions_px
        self.surface = pygame.display.set_mode(self.dimensions_px)
        self.erase_and_update()  # Updates the screen for the first time.

        # Limits the frame rate and assigns a clock to control it.
        self.frame_rate_limit = 100
        self.clock = pygame.time.Clock()

        self.is_scrolling = False    # Will be set true when the player is high enough so the screen can begin scrolling.
        self.scrolling_rate_mps = 5  # Controls the scrolling rate of the screen.

        self.done = False          # Will exit the loop when the player loses or decides to quit.

    def erase_and_update(self):
        self.set_background()
        pygame.display.flip()

    @staticmethod
    def invert(color):
        a, b, c, d = color
        return abs(a - 255), abs(b - 255), abs(c - 255), abs(d - 255)

    def random_color_name(self):
        color_name = random.choice(THECOLORS.keys())
        if color_name == self.curr_color_name or color_name == self.background_color:
            return self.random_color_name()
        return color_name

    def set_background(self):
        self.surface.fill(self.background_color)

    def get_user_input(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_RIGHT]:
            self.air_track.player.move_right()
            self.air_track.player.time_moving_to_side += self.session.dt_s
            self.air_track.player.time_since_last_side_movement = 0
        elif pressed_keys[pygame.K_LEFT]:
            self.air_track.player.move_left()
            self.air_track.player.time_moving_to_side += self.session.dt_s
            self.air_track.player.time_since_last_side_movement = 0
        else:
            self.air_track.player.time_moving_to_side = 0
            self.air_track.player.time_since_last_side_movement += self.session.dt_s

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.air_track.player.is_jumping = True

    def draw_objects(self):
        """
        Draws all the objects on the screen.
        """
        game_window.air_track.player.draw()
        for step in self.air_track.steps:
            step.draw()

    def show_score(self):
        score = self.hud_font.render("Score: {}".format(self.session.score), 1, THECOLORS['white'])
        self.surface.blit(score, (self.width_px - 200, 50))
        rate = self.hud_font.render("Rate: {}".format(self.get_scroll_rate_mps()), 1, THECOLORS['white'])
        self.surface.blit(rate, (self.width_px - 200, 100))

    def control_screen_scrolling(self):
        """
        Starts scrolling of the screen if needed, and scrolls it for each framerate.
        """
        if not self.is_scrolling:
            if float(self.air_track.player.position.y_m) < self.env.height_m / 2:
                self.is_scrolling = True
        if self.is_scrolling:
            self.scroll()

    def keep_player_at_the_middle(self):
        if self.is_scrolling:
            if self.air_track.player.position.y_m < self.env.height_m / 2:
                deviation_m = self.env.height_m / 2 - self.air_track.player.position.y_m
                self.air_track.player.position.y_m += deviation_m
                for step in self.air_track.steps:
                    step.center_m.y_m += deviation_m

    def get_scroll_rate_mps(self):
        try:
            return self.scrolling_rate_mps * (self.session.score / pow(self.session.score, 0.7))
        except ZeroDivisionError:
            return self.scrolling_rate_mps

    def scroll(self):
        """
        Scrolls the screen by lowering the position of all the object by the specified rate.
        """
        self.air_track.player.position. y_m += self.get_scroll_rate_mps() * self.session.dt_s
        for step in self.air_track.steps:
            step.center_m.y_m += self.get_scroll_rate_mps() * self.session.dt_s

    def loop(self):
        """
        Mainloop function, updates each frame
        """
        while not self.done:
            self.set_background()
            self.session.dt_s = float(self.clock.tick(self.frame_rate_limit) * 1e-3)  # Get the delta t for one frame rate (this changes depending on system load)
            self.get_user_input()              # Gets any user input
            self.control_screen_scrolling()    # Controlling the screen's scrolling rate
            self.keep_player_at_the_middle()
            self.air_track.player.update()     # Updates the player's position
            self.air_track.update_steps()      # Deleting steps that are lower than the floor, and generating new steps
            self.draw_objects()                # Drawing the player and the steps
            self.show_score()
            if self.air_track.player.top_vertex().y_m > self.env.height_m:  # If the player is lower than the floor, ends the loop
                self.done = True

            self.session.advance_time()  # Advancing in time
            pygame.display.flip()        # Showing the screen


# ==================
# Dimensional Classes
# ==================


class Position:

    def __init__(self, x_m, y_m):
        """
        Position object, consisted of x and y measured in meters.
        :param x_m: Position in meters on x axis.
        :param y_m: Position in meters on y axis.
        """
        self.x_m = float(x_m)
        self.y_m = float(y_m)

    def coordinates_m(self):
        return self.x_m, self.y_m

    def coordinates_px(self, m_to_px_ratio):
        return int(self.x_m * m_to_px_ratio), int(self.y_m * m_to_px_ratio)

    def set_x_m(self, x_m):
        self.x_m = float(x_m)

    def set_y_mps(self, y_m):
        self.y_m = float(y_m)


class Vector:

    def __init__(self, x_mps, y_mps):
        """
        Vector object, consisted of x and y measured in meters/seconds^2.
        :param x_mps: Speed in mps on x axis.
        :param y_mps: Speed in mps on y axis.
        """
        self.x_mps = float(x_mps)
        self.y_mps = float(y_mps)

    def set_x_mps(self, x_mps):
        self.x_mps = float(x_mps)

    def set_y_mps(self, y_mps):
        self.y_mps = float(y_mps)


class Environment:

    def __init__(self, width_m, height_m, width_px):
        """
        The environment object controls the world the game takes place in.
        :param width_m: Game world width in meters.
        :param height_m:
        :param width_px:
        """
        self.gravity_mps2 = 200
        self.dimensions_m = self.width_m, self.height_m = float(width_m), float(height_m)
        self.m_to_px_ratio = width_px / self.width_m
        self.dimensions_px = self.width_px, self.height_px = width_px, self.m_to_px(self.height_m)

    def m_to_px(self, m):
        return int(m * self.m_to_px_ratio)


class AirTrack:

    def __init__(self, window):
        """
        The air track controls the objects that appear on the screen.
        :param window: Pygame window.
        """
        self.window = window
        self.player = Player(self.window)
        self.step_id = 1
        self.steps_num = 5
        self.steps = []
        self.draw_steps()

    def draw_steps(self):
        """
        This method initializes the right amount of steps for the beginning of the game.
        """

        # Sets the floor step (the one the player stand on at the beginning of the game).
        floor_step = Step(self.window, 0)
        floor_step.center_m.y_m = self.window.env.height_m
        floor_step.length_m = 1000
        self.steps.append(floor_step)

        # Assigns margins between steps and appends the steps to the steps list.
        margins_m = int(self.window.env.height_m / self.steps_num)
        y_positions_m = range(int(self.window.env.height_m) - margins_m, 0, -margins_m)
        for y_pos_m in y_positions_m:
            s = Step(self.window, self.step_id)
            s.center_m.y_m = y_pos_m
            self.steps.append(s)
            self.step_id += 1

    def update_steps(self):
        """
        This method validates that there are always the specified amount of steps on the screen.
        """
        for step in self.steps:
            if step.center_m.y_m > self.window.env.height_m:
                self.steps.remove(step)
                del step
        if len(self.steps) < self.steps_num:
            s = Step(self.window, self.step_id)
            if self.step_id % 50 == 0:
                s.length_m = 1000
            if self.step_id % 100 == 0:
                self.window.step_color = THECOLORS[self.window.random_color_name()]
            if self.step_id % 10 == 0:
                s.should_draw_score = True
            s.center_m.y_m = 0
            self.steps.append(s)
            self.step_id += 1

# ==================
# Object Classes
# ==================


class Step:

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
        floor_num = self.window.hud_font.render(str(self.id), 1, self.window.invert(self.color))
        w, h = self.center_m.coordinates_px(self.window.env.m_to_px_ratio)
        self.window.surface.blit(floor_num, (w, h))

    def draw(self):
        pygame.draw.line(self.window.surface, self.color, self.left_edge().coordinates_px(self.window.env.m_to_px_ratio), self.right_edge().coordinates_px(self.window.env.m_to_px_ratio), 3)
        if self.should_draw_score:
            self.draw_score()


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


# ==================
# Main
# ==================


if __name__ == '__main__':
    e = Environment(70, 50, 1000)
    game_window = GameWindow(e)
    game_window.loop()
