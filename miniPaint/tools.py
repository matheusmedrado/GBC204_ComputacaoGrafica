import math

from fill import flood_fill
from raster import draw_circle, draw_line
from shapes import Circle, Line, Polygon


class Style:
    def __init__(self, color=(0, 0, 0), size=1, filled=False):
        self.color = color
        self.size = size
        self.filled = filled

    def copy(self):
        return Style(self.color, self.size, self.filled)


class Tool:
    name = ""
    shortcut = ""
    uses_fill = False
    keeps_selection = False

    def __init__(self, style):
        self.style = style

    @property
    def uses_size(self):
        # Forma preenchida não tem contorno, então a espessura não vale pra ela
        return not (self.uses_fill and self.style.filled)

    # press, release e enter podem devolver uma forma pronta, que vira a forma selecionada
    def press(self, canvas, x, y):
        pass

    def drag(self, canvas, x, y):
        pass

    def release(self, canvas, x, y):
        pass

    def hover(self, x, y):
        pass

    def enter(self):
        return None

    def cancel(self):
        pass

    def preview(self, screen):
        pass


class Brush(Tool):
    name = "Pincel"
    shortcut = "I"

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
    shortcut = "P"
    uses_size = False

    def size(self):
        return 1


class Eraser(Brush):
    name = "Borracha"
    shortcut = "B"

    def color(self, canvas):
        return canvas.background


class ShapeTool(Tool):
    # Clicar marca o começo, arrastar mostra a prévia e soltar entrega a forma pronta
    def __init__(self, style):
        super().__init__(style)
        self.start = self.end = None

    def press(self, canvas, x, y):
        self.start = self.end = (x, y)

    def drag(self, canvas, x, y):
        self.end = (x, y)

    def release(self, canvas, x, y):
        self.end = (x, y)
        shape = self.make()
        self.start = self.end = None
        return shape

    def preview(self, screen):
        if self.start:
            self.make().draw(screen)

    def make(self):
        pass


class LineTool(ShapeTool):
    name = "Linha"
    shortcut = "L"

    def make(self):
        return Line([self.start, self.end], self.style.copy())


class RectTool(ShapeTool):
    name = "Retângulo"
    shortcut = "R"
    uses_fill = True

    def make(self):
        (x0, y0), (x1, y1) = self.start, self.end
        return Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], self.style.copy())


class CircleTool(ShapeTool):
    name = "Círculo"
    shortcut = "C"
    uses_fill = True

    def make(self):
        # O clique marca o centro, e o ponto onde o mouse está fica na borda
        return Circle([self.start, self.end], self.style.copy())


class PolygonTool(Tool):
    name = "Polígono"
    shortcut = "G"
    uses_fill = True

    def __init__(self, style):
        super().__init__(style)
        self.vertices = []
        self.cursor = None

    def press(self, canvas, x, y):
        # Clicar perto do primeiro ponto fecha a figura
        if len(self.vertices) >= 3 and math.dist((x, y), self.vertices[0]) <= 8:
            return self.enter()
        self.vertices.append((x, y))

    def drag(self, canvas, x, y):
        self.cursor = (x, y)

    def hover(self, x, y):
        self.cursor = (x, y)

    def enter(self):
        if len(self.vertices) < 3:
            return None
        shape = Polygon(self.vertices, self.style.copy())
        self.vertices = []
        return shape

    def cancel(self):
        self.vertices = []

    def preview(self, screen):
        if not self.vertices:
            return
        points = self.vertices + [self.cursor or self.vertices[-1]]
        for a, b in zip(points, points[1:]):
            draw_line(screen, *a, *b, self.style.color, self.style.size)
        draw_circle(screen, *self.vertices[0], 6, self.style.color)


class Bucket(Tool):
    name = "Balde"
    shortcut = "F"
    uses_size = False

    def press(self, canvas, x, y):
        flood_fill(canvas, x, y, self.style.color)


class MoveTool(Tool):
    name = "Mover"
    shortcut = "M"
    uses_size = False
    keeps_selection = True

    def __init__(self, app):
        super().__init__(app.style)
        self.app = app
        self.last = None

    def press(self, canvas, x, y):
        # Clicar dentro da moldura pega a forma; clicar fora fixa ela no desenho
        box = self.app.selection_box()
        if box and box[0] <= x <= box[2] and box[1] <= y <= box[3]:
            self.last = (x, y)
        else:
            self.last = None
            self.app.commit_selection()

    def drag(self, canvas, x, y):
        if self.last:
            self.app.move_selection(x - self.last[0], y - self.last[1])
            self.last = (x, y)
