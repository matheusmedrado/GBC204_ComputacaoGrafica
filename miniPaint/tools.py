import math

from fill import flood_fill
from raster import draw_circle, draw_line, draw_rect, fill_circle, fill_rect


class Style:
    def __init__(self, color=(0, 0, 0), size=1, filled=False):
        self.color = color
        self.size = size
        self.filled = filled


class Tool:
    name = ""

    def __init__(self, style):
        self.style = style

    def press(self, canvas, x, y):
        pass

    def drag(self, canvas, x, y):
        pass

    def release(self, canvas, x, y):
        pass

    def preview(self, screen):
        pass


class Brush(Tool):
    name = "Pincel"

    def color(self, canvas):
        return self.style.color

    def size(self):
        return self.style.size

    def press(self, canvas, x, y):
        self.last = (x, y)
        draw_line(canvas, x, y, x, y, self.color(canvas), self.size())

    def drag(self, canvas, x, y):
        # O mouse só avisa algumas posições por segundo, então ligamos a última à atual
        draw_line(canvas, *self.last, x, y, self.color(canvas), self.size())
        self.last = (x, y)


class Pencil(Brush):
    name = "Lápis"

    def size(self):
        return 1


class Eraser(Brush):
    name = "Borracha"

    def color(self, canvas):
        return canvas.background


class Shape(Tool):
    # Clicar marca o começo, arrastar mostra a prévia e soltar grava no canvas
    def __init__(self, style):
        super().__init__(style)
        self.start = self.end = None

    def press(self, canvas, x, y):
        self.start = self.end = (x, y)

    def drag(self, canvas, x, y):
        self.end = (x, y)

    def release(self, canvas, x, y):
        self.end = (x, y)
        self.draw(canvas)
        self.start = self.end = None

    def preview(self, screen):
        if self.start:
            self.draw(screen)

    def draw(self, fb):
        pass


class Line(Shape):
    name = "Linha"

    def draw(self, fb):
        draw_line(fb, *self.start, *self.end, self.style.color, self.style.size)


class Rect(Shape):
    name = "Retângulo"

    def draw(self, fb):
        if self.style.filled:
            fill_rect(fb, *self.start, *self.end, self.style.color)
        else:
            draw_rect(fb, *self.start, *self.end, self.style.color, self.style.size)


class Circle(Shape):
    name = "Círculo"

    def draw(self, fb):
        # O clique marca o centro, e o raio vai até onde o mouse está
        (cx, cy), (x, y) = self.start, self.end
        r = round(math.hypot(x - cx, y - cy))
        if self.style.filled:
            fill_circle(fb, cx, cy, r, self.style.color)
        else:
            draw_circle(fb, cx, cy, r, self.style.color, self.style.size)


class Bucket(Tool):
    name = "Balde"

    def press(self, canvas, x, y):
        flood_fill(canvas, x, y, self.style.color)
