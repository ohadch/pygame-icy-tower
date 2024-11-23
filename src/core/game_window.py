import random

import pygame
from pygame.color import THECOLORS

from src.core.air_track import AirTrack
from src.core.serssion import Session


class GameWindow:

    def __init__(self, environment):
        """
        Controls the UI, in this case Pygame window.
        :param environment: Environment object.
        """

        # Colors
        self.background_color = THECOLORS['black']
        self.curr_color_name = random.choice(list(THECOLORS.keys()))
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
        color_name = random.choice(list(THECOLORS.keys()))
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
        self.air_track.player.draw()
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
