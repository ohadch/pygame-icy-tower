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
