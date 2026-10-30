import numpy as np


def blend(a, b, t):
    # Mistura duas cores: t é quanto da segunda entra, de 0 a 1
    return tuple(round(ca * (1 - t) + cb * t) for ca, cb in zip(a, b))


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

    def put_image(self, x, y, image, mask):
        # Cola só os pontos marcados da imagem, cortando o que cair fora da tela
        h, w = mask.shape
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.width), min(y + h, self.height)
        if x0 < x1 and y0 < y1:
            visible = mask[y0 - y:y1 - y, x0 - x:x1 - x]
            self.pixels[y0:y1, x0:x1][visible] = image[y0 - y:y1 - y, x0 - x:x1 - x][visible]

    def snapshot(self):
        return self.pixels.copy()

    def restore(self, snapshot):
        self.pixels[:] = snapshot

    def matches(self, snapshot):
        return np.array_equal(self.pixels, snapshot)
