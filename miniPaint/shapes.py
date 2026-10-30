import math

import numpy as np

from raster import draw_circle, draw_line, draw_polygon, fill_circle, fill_polygon
from transform import apply, inverse, multiply, translation


class Shape:
    def __init__(self, points, style):
        # Os pontos ficam com casas decimais pra giros seguidos não acumularem arredondamento
        self.points = [(float(x), float(y)) for x, y in points]
        self.style = style

    def pixels(self):
        return [(round(x), round(y)) for x, y in self.points]

    def center(self):
        # A média dos pontos, como sugere o slide da rotação em volta do centro
        xs, ys = zip(*self.points)
        return sum(xs) / len(xs), sum(ys) / len(ys)

    def transform(self, m):
        self.points = apply(m, self.points)

    def bounds(self):
        xs, ys = zip(*self.pixels())
        pad = self.style.size // 2
        return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad

    def draw(self, fb):
        pass


class Line(Shape):
    def draw(self, fb):
        (x0, y0), (x1, y1) = self.pixels()
        draw_line(fb, x0, y0, x1, y1, self.style.color, self.style.size)


class Polygon(Shape):
    def draw(self, fb):
        if self.style.filled:
            fill_polygon(fb, self.pixels(), self.style.color)
        else:
            draw_polygon(fb, self.pixels(), self.style.color, self.style.size)


class Circle(Shape):
    # Guarda o centro e um ponto da borda; transformando os dois, o círculo move, gira e escala junto
    def center(self):
        return self.points[0]

    def radius(self):
        (cx, cy), (x, y) = self.points
        return math.hypot(x - cx, y - cy)

    def bounds(self):
        cx, cy = self.pixels()[0]
        r = round(self.radius()) + self.style.size // 2
        return cx - r, cy - r, cx + r, cy + r

    def draw(self, fb):
        cx, cy = self.pixels()[0]
        if self.style.filled:
            fill_circle(fb, cx, cy, round(self.radius()), self.style.color)
        else:
            draw_circle(fb, cx, cy, round(self.radius()), self.style.color, self.style.size)


class Patch(Shape):
    # Um pedaço retangular do desenho que descolou do canvas
    def __init__(self, pixels, x, y, style):
        h, w = pixels.shape[:2]
        super().__init__([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], style)
        self.source = pixels
        self.matrix = translation(x, y)
        self.cache = None

    def transform(self, m):
        super().transform(m)
        self.matrix = multiply(self.matrix, m)
        # Arrastar só desloca a imagem já montada; girar ou escalar precisa montar de novo
        dx, dy = m[2][0], m[2][1]
        if self.cache and m[0][:2] == [1, 0] and m[1][:2] == [0, 1] and dx == int(dx) and dy == int(dy):
            x0, y0, image, mask = self.cache
            self.cache = (x0 + int(dx), y0 + int(dy), image, mask)
        else:
            self.cache = None

    def bounds(self):
        xs, ys = zip(*self.points)
        return math.floor(min(xs)), math.floor(min(ys)), math.ceil(max(xs)) - 1, math.ceil(max(ys)) - 1

    def render(self):
        # Pra cada pixel do destino, a matriz inversa diz de qual pixel do pedaço original ele veio
        (a, b, _), (c, d, _), (e, f, _) = inverse(self.matrix)
        x0, y0, x1, y1 = self.bounds()
        h, w = self.source.shape[:2]
        source = self.source.tolist()
        image = np.zeros((y1 - y0 + 1, x1 - x0 + 1, 3), np.uint8)
        mask = np.zeros((y1 - y0 + 1, x1 - x0 + 1), bool)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                # Usa o centro do pixel, que fica meio pixel pra dentro do canto
                sx = math.floor((x + 0.5) * a + (y + 0.5) * c + e)
                sy = math.floor((x + 0.5) * b + (y + 0.5) * d + f)
                if 0 <= sx < w and 0 <= sy < h:
                    image[y - y0, x - x0] = source[sy][sx]
                    mask[y - y0, x - x0] = True
        return x0, y0, image, mask

    def draw(self, fb):
        if self.cache is None:
            self.cache = self.render()
        fb.put_image(*self.cache)
