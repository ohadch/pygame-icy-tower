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
