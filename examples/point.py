"""
Example symbolic execution with object wrapping
"""

TOP_RIGHT_QUAD    = 1
BOTTOM_RIGHT_QUAD = 2
BOTTOM_LEFT_QUAD  = 3
TOP_LEFT_QUAD     = 4

class Point:
    """ Create a new Point, at coordinates x, y """

    def __init__(self, x=0, y=0):
        """ Create a new point at x, y """
        self.x = x
        self.y = y

    def reflect_x(self):
        return Point(self.x, -self.y)

    def reflect_y(self):
        return Point(-self.x, self.y)

    def quadrant(self):
        if self.x >= 0 and self.y >= 0:
            return TOP_RIGHT_QUAD
        elif self.x >= 0 and self.y < 0:
            return BOTTOM_RIGHT_QUAD
        elif self.x < 0 and self.y < 0:
            return BOTTOM_LEFT_QUAD
        else:
            return TOP_LEFT_QUAD

def test(p):
    """ 
    We want to symbolically execute this
    function but it takes in a point. 
    """
    while p.quadrant() != TOP_RIGHT_QUAD:
        if p.x < 0:
            p = p.reflect_y()
        else:
            p = p.reflect_x()
    return p

def point(x, y):
    """
    Wrap test so that we can symbolically execute it
    """
    return test(Point(x,y))