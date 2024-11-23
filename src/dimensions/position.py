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
