from pygame import init, display, DOUBLEBUF, HWSURFACE, FULLSCREEN, RESIZABLE

class Screen():
    """
    A class used to implement a screen

    Attributes
    ----------
    bg_color: tuple
        Background color in RGB
    res: tuple
        Screen resolution in pixels
    opt: int
        Screen options
    """
    def __init__(self, resolution):
        init()
        self.resolution = resolution
        self.__bg_color = (200, 200, 200)
        # self.__res = (display.Info().current_h, display.Info().current_h)
        self.__res = (display.Info().current_h - 68, display.Info().current_h - 68)
        # self.__opt = DOUBLEBUF | HWSURFACE | FULLSCREEN
        self.__opt = DOUBLEBUF | HWSURFACE
        
    @property
    def bg_color(self):
        """This is bg_color property"""
        return self.__bg_color
    
    @property
    def res(self):
        """This is res property"""
        return self.__res
    
    @property
    def opt(self):
        """This is opt property"""
        return self.__opt

    @property
    def width(self):
        """This is width property"""
        return self.__res[0] + self.resolution
    
    @property
    def height(self):
        """This is height property"""
        return self.__res[1]

    @property
    def width_middle(self):
        """This is width_middle property"""
        return self.width // 2
    
    @property
    def height_middle(self):
        """This is height_middle property"""
        return self.height // 2

    @property
    def left_top(self):
        """This is left_top property"""
        return (0 + self.resolution, 0)

    @property
    def middle_top(self):
        """This is middle_top property"""
        return (self.width_middle, 0)

    @property
    def right_top(self):
        """This is right_top property"""
        return (self.width, 0)

    @property
    def right_middle(self):
        """This is right_middle property"""
        return (self.width, self.height_middle)
    
    @property
    def right_bottom(self):
        """This is right_bottom property"""
        return (self.width, self.height)

    @property
    def middle_bottom(self):
        """This is middle_bottom property"""
        return (self.width_middle, self.height)

    @property
    def left_bottom(self):
        """This is left_bottom property"""
        return (0 + self.resolution, self.height)

    @property
    def left_middle(self):
        """This is left_middle property"""
        return (0 + self.resolution, self.height_middle)

    @property
    def middle(self):
        """This is middle property"""
        return (self.width_middle, self.height_middle)