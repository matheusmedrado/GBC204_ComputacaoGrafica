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
        return tuple(self.pixels[y, x].tolist())

    def put_span(self, x0, x1, y, color):
        # Um trecho horizontal de uma vez: dá no mesmo que put_pixel em cada x, só que bem mais rápido
        x0, x1 = max(min(x0, x1), 0), min(max(x0, x1), self.width - 1)
        if 0 <= y < self.height and x0 <= x1:
            self.pixels[y, x0:x1 + 1] = color

    def clear(self, color=None):
        self.pixels[:] = color or self.background

    def copy_from(self, other):
        self.pixels[:] = other.pixels
