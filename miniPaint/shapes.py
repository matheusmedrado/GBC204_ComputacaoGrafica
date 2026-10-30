import math

from raster import draw_circle, draw_line, draw_polygon, fill_circle, fill_polygon
from transform import apply


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
