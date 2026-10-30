from raster import draw_line


class Style:
    def __init__(self, color=(0, 0, 0), size=1):
        self.color = color
        self.size = size


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


class Line(Tool):
    name = "Linha"

    def __init__(self, style):
        super().__init__(style)
        self.start = self.end = None

    def press(self, canvas, x, y):
        self.start = self.end = (x, y)

    def drag(self, canvas, x, y):
        self.end = (x, y)

    def release(self, canvas, x, y):
        draw_line(canvas, *self.start, x, y, self.style.color, self.style.size)
        self.start = self.end = None

    def preview(self, screen):
        if self.start:
            draw_line(screen, *self.start, *self.end, self.style.color, self.style.size)
