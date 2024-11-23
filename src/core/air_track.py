from pygame.color import THECOLORS

from src.entities.player import PlayerEntity
from src.entities.step import StepEntity


class AirTrack:

    def __init__(self, window):
        """
        The air track controls the objects that appear on the screen.
        :param window: Pygame window.
        """
        self.window = window
        self.player = PlayerEntity(self.window)
        self.step_id = 1
        self.steps_num = 5
        self.steps = []
        self.draw_steps()

    def draw_steps(self):
        """
        This method initializes the right amount of steps for the beginning of the game.
        """

        # Sets the floor step (the one the player stand on at the beginning of the game).
        floor_step = StepEntity(self.window, 0)
        floor_step.center_m.y_m = self.window.env.height_m
        floor_step.length_m = 1000
        self.steps.append(floor_step)

        # Assigns margins between steps and appends the steps to the steps list.
        margins_m = int(self.window.env.height_m / self.steps_num)
        y_positions_m = range(int(self.window.env.height_m) - margins_m, 0, -margins_m)
        for y_pos_m in y_positions_m:
            s = StepEntity(self.window, self.step_id)
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
            s = StepEntity(self.window, self.step_id)
            if self.step_id % 50 == 0:
                s.length_m = 1000
            if self.step_id % 100 == 0:
                self.window.step_color = THECOLORS[self.window.random_color_name()]
            if self.step_id % 10 == 0:
                s.should_draw_score = True
            s.center_m.y_m = 0
            self.steps.append(s)
            self.step_id += 1
