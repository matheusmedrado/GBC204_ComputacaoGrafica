from framebuffer import Framebuffer, blend
from raster import circle_points, draw_circle, draw_line, draw_rect, fill_circle, fill_rect

TOOLBAR_WIDTH = 84
SIZES = {"fino": 1, "médio": 5, "grosso": 11}
PALETTE = [
    ("Preto", (0, 0, 0)), ("Branco", (255, 255, 255)),
    ("Vermelho", (255, 0, 0)), ("Verde", (0, 255, 0)),
    ("Azul", (0, 0, 255)), ("Amarelo", (255, 255, 0)),
    ("Ciano", (0, 255, 255)), ("Magenta", (255, 0, 255)),
]

MARGIN, GAP, SECTION_GAP = 8, 4, 13
BAR = (205, 208, 214)
BUTTON = (238, 240, 244)
HOVER = (224, 228, 236)
ACTIVE = (196, 216, 255)
BORDER = (150, 155, 165)
ACTIVE_BORDER = (40, 100, 220)
INK = (30, 30, 30)


def pencil_icon(fb, cx, cy):
    draw_line(fb, cx + 8, cy - 8, cx + 6, cy - 6, (255, 170, 185), 5)
    draw_line(fb, cx + 5, cy - 5, cx - 4, cy + 4, (245, 190, 40), 5)
    draw_line(fb, cx - 5, cy + 5, cx - 7, cy + 7, (230, 200, 160), 3)
    draw_line(fb, cx - 8, cy + 8, cx - 9, cy + 9, INK)


def brush_icon(fb, cx, cy):
    draw_line(fb, cx + 9, cy - 9, cx + 2, cy - 2, (150, 95, 50), 3)
    draw_line(fb, cx + 1, cy - 1, cx - 2, cy + 2, (170, 172, 180), 5)
    fill_circle(fb, cx - 5, cy + 5, 3, INK)
    draw_line(fb, cx - 5, cy + 5, cx - 9, cy + 9, INK, 3)


def eraser_icon(fb, cx, cy):
    fill_rect(fb, cx - 9, cy - 5, cx + 9, cy + 5, (255, 180, 195))
    draw_rect(fb, cx - 9, cy - 5, cx + 9, cy + 5, INK)


def line_icon(fb, cx, cy):
    draw_line(fb, cx - 9, cy + 7, cx + 9, cy - 7, INK)
    fill_circle(fb, cx - 9, cy + 7, 2, INK)
    fill_circle(fb, cx + 9, cy - 7, 2, INK)


def rect_icon(fb, cx, cy):
    draw_rect(fb, cx - 10, cy - 7, cx + 10, cy + 7, INK)


def circle_icon(fb, cx, cy):
    draw_circle(fb, cx, cy, 9, INK)


def bucket_icon(style):
    def icon(fb, cx, cy):
        # A alça é só a metade de cima de um círculo
        for x, y in circle_points(cx - 2, cy - 1, 6):
            if y <= cy - 1:
                fb.put_pixel(x, y, INK)
        fill_rect(fb, cx - 8, cy - 1, cx + 4, cy + 9, style.color)
        draw_rect(fb, cx - 8, cy - 1, cx + 4, cy + 9, INK)
        fill_circle(fb, cx + 8, cy + 5, 2, style.color)
        draw_circle(fb, cx + 8, cy + 5, 2, INK)
    return icon


def outline_icon(fb, cx, cy):
    draw_rect(fb, cx - 8, cy - 6, cx + 8, cy + 6, INK)


def filled_icon(fb, cx, cy):
    fill_rect(fb, cx - 8, cy - 6, cx + 8, cy + 6, INK)


def thickness_icon(size):
    def icon(fb, cx, cy):
        draw_line(fb, cx - 24, cy, cx + 24, cy, INK, size)
    return icon


def swatch_icon(color):
    def icon(fb, cx, cy):
        fill_rect(fb, cx - 11, cy - 7, cx + 11, cy + 7, color)
        draw_rect(fb, cx - 11, cy - 7, cx + 11, cy + 7, BORDER)
    return icon


def new_icon(fb, cx, cy):
    fill_rect(fb, cx - 7, cy - 9, cx + 7, cy + 9, (255, 255, 255))
    draw_rect(fb, cx - 7, cy - 9, cx + 7, cy + 9, INK)
    draw_line(fb, cx + 2, cy - 9, cx + 7, cy - 4, INK)


def save_icon(fb, cx, cy):
    fill_rect(fb, cx - 9, cy - 9, cx + 9, cy + 9, (60, 90, 160))
    fill_rect(fb, cx - 5, cy - 9, cx + 4, cy - 4, (200, 205, 215))
    fill_rect(fb, cx + 1, cy - 8, cx + 3, cy - 5, (60, 90, 160))
    fill_rect(fb, cx - 6, cy + 1, cx + 6, cy + 7, (255, 255, 255))


class Button:
    def __init__(self, x, y, w, h, label, icon, on_click, is_active, applies):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.label = label
        self.icon = icon
        self.on_click = on_click
        self.is_active = is_active
        self.applies = applies

    def contains(self, x, y):
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def draw(self, fb, hovered):
        x0, y0, x1, y1 = self.x, self.y, self.x + self.w - 1, self.y + self.h - 1
        active = self.is_active()
        fill_rect(fb, x0, y0, x1, y1, ACTIVE if active else HOVER if hovered else BUTTON)
        draw_rect(fb, x0, y0, x1, y1, ACTIVE_BORDER if active else BORDER, 3 if active else 1)
        self.icon(fb, self.x + self.w // 2, self.y + self.h // 2)

        if not self.applies():
            # A opção não vale pra ferramenta atual: o botão se mistura com o fundo da barra
            for y in range(y0 - 1, y1 + 2):
                for x in range(x0 - 1, x1 + 2):
                    fb.put_pixel(x, y, blend(fb.get_pixel(x, y), BAR, 0.65))


class Toolbar:
    def __init__(self, app, width, height):
        self.fb = Framebuffer(width, height, BAR)
        self.buttons = []
        self.separators = []
        self.last_state = None
        self.y = MARGIN

        icons = {
            "Lápis": pencil_icon, "Pincel": brush_icon, "Borracha": eraser_icon,
            "Linha": line_icon, "Retângulo": rect_icon, "Círculo": circle_icon, "Balde": bucket_icon(app.style),
        }
        # O t=t prende cada ferramenta no seu botão; sem isso, todos ficariam com a última do laço
        self.add_section(2, 32, [
            (f"{t.name} ({t.shortcut})", icons[t.name], lambda t=t: app.select_tool(t), lambda t=t: app.tool is t)
            for t in app.tools
        ])
        self.add_section(2, 28, [
            ("Vazado (V)", outline_icon, lambda: app.set_filled(False), lambda: not app.style.filled),
            ("Preenchido (V)", filled_icon, lambda: app.set_filled(True), lambda: app.style.filled),
        ], applies=lambda: app.tool.uses_fill)
        self.add_section(1, 18, [
            (f"{name.capitalize()} ({i + 1})", thickness_icon(px),
             lambda n=name: app.set_size(n), lambda n=name: app.size_name == n)
            for i, (name, px) in enumerate(SIZES.items())
        ], applies=lambda: app.tool.uses_size)
        self.add_section(2, 24, [
            (name, swatch_icon(c), lambda c=c: app.set_color(c), lambda c=c: app.style.color == c)
            for name, c in PALETTE
        ])
        self.add_section(2, 32, [
            ("Novo (N)", new_icon, app.new_drawing, lambda: False),
            ("Salvar (S)", save_icon, app.save, lambda: False),
        ])

    def add_section(self, cols, h, items, applies=lambda: True):
        w = (self.fb.width - 2 * MARGIN - GAP * (cols - 1)) // cols
        for i, (label, icon, on_click, is_active) in enumerate(items):
            x = MARGIN + (i % cols) * (w + GAP)
            y = self.y + (i // cols) * (h + GAP)
            self.buttons.append(Button(x, y, w, h, label, icon, on_click, is_active, applies))
        rows = (len(items) + cols - 1) // cols
        self.y += rows * (h + GAP) - GAP + SECTION_GAP
        self.separators.append(self.y - SECTION_GAP // 2 - 1)

    def button_at(self, x, y):
        for button in self.buttons:
            if button.contains(x, y):
                return button
        return None

    def click(self, x, y):
        button = self.button_at(x, y)
        if button:
            button.on_click()

    def draw(self, mouse):
        # Só redesenha quando muda o botão sob o mouse ou o estado de algum botão
        state = (self.button_at(*mouse), [(b.is_active(), b.applies()) for b in self.buttons])
        if state == self.last_state:
            return
        self.last_state = state

        fb = self.fb
        fb.clear()
        draw_line(fb, fb.width - 1, 0, fb.width - 1, fb.height - 1, BORDER)
        for y in self.separators[:-1]:
            draw_line(fb, MARGIN, y, fb.width - MARGIN - 1, y, BORDER)
        for button in self.buttons:
            button.draw(fb, button.contains(*mouse))
