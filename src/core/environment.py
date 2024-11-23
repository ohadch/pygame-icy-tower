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
