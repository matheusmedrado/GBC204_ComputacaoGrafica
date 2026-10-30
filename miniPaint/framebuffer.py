import numpy as np


class Framebuffer:
    def __init__(self, width, height, background=(255, 255, 255)):
        self.width = width
        self.height = height
        self.background = background
        # Uma linha da matriz por linha da tela, e cada pixel guarda vermelho, verde e azul de 0 a 255
        self.pixels = np.zeros((height, width, 3), dtype=np.uint8)
        self.clear()

    def inside(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def put_pixel(self, x, y, color):
        if self.inside(x, y):
            self.pixels[y, x] = color

    def get_pixel(self, x, y):
        if not self.inside(x, y):
            return None
        r, g, b = self.pixels[y, x]
        return (int(r), int(g), int(b))

    def clear(self, color=None):
        self.pixels[:] = color or self.background

    def copy_from(self, other):
        self.pixels[:] = other.pixels
