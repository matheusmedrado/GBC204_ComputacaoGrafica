from raster import draw_line


class Brush:
    def __init__(self, color=(0, 0, 0), size=1):
        self.color = color
        self.size = size


class Tool:
    name = ""

    def __init__(self, brush):
        self.brush = brush

    def press(self, canvas, x, y):
        pass

    def drag(self, canvas, x, y):
        pass

    def release(self, canvas, x, y):
        pass

    def preview(self, screen):
        pass


class Pencil(Tool):
    name = "Lápis"

    def color(self, canvas):
        return self.brush.color

    def press(self, canvas, x, y):
        self.last = (x, y)
        draw_line(canvas, x, y, x, y, self.color(canvas), self.brush.size)

    def drag(self, canvas, x, y):
        # O mouse só avisa algumas posições por segundo, então ligamos a última à atual
        draw_line(canvas, *self.last, x, y, self.color(canvas), self.brush.size)
        self.last = (x, y)


class Eraser(Pencil):
    name = "Borracha"

    def color(self, canvas):
        return canvas.background


class Line(Tool):
    name = "Linha"

    def __init__(self, brush):
        super().__init__(brush)
        self.start = self.end = None

    def press(self, canvas, x, y):
        self.start = self.end = (x, y)

    def drag(self, canvas, x, y):
        self.end = (x, y)

    def release(self, canvas, x, y):
        draw_line(canvas, *self.start, x, y, self.brush.color, self.brush.size)
        self.start = self.end = None

    def preview(self, screen):
        if self.start:
            draw_line(screen, *self.start, *self.end, self.brush.color, self.brush.size)
