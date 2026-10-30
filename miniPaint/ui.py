from framebuffer import Framebuffer, blend
from raster import (circle_points, draw_circle, draw_dashed_rect, draw_line, draw_polygon, draw_rect,
                    fill_circle, fill_polygon, fill_rect, stamp)

TOOLBAR_WIDTH = 84
SIZES = {"fino": 1, "médio": 5, "grosso": 11}
ROTATION_STEP, SCALE_STEP = 15, 1.1
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
WHITE = (255, 255, 255)
METAL = (170, 172, 180)
SHAPE_FILL = (200, 222, 250)
SHAPE_LINE = (40, 90, 170)
GREEN = (40, 160, 80)
RED = (210, 50, 50)


def pencil_icon(fb, cx, cy):
    draw_line(fb, cx + 8, cy - 8, cx + 6, cy - 6, (255, 170, 185), 5)
    draw_line(fb, cx + 5, cy - 5, cx - 4, cy + 4, (245, 190, 40), 5)
    draw_line(fb, cx - 5, cy + 5, cx - 7, cy + 7, (230, 200, 160), 3)
    draw_line(fb, cx - 8, cy + 8, cx - 9, cy + 9, INK)


def brush_icon(fb, cx, cy):
    draw_line(fb, cx + 9, cy - 9, cx + 2, cy - 2, (150, 95, 50), 3)
    draw_line(fb, cx + 1, cy - 1, cx - 2, cy + 2, METAL, 5)
    fill_circle(fb, cx - 5, cy + 5, 3, INK)
    draw_line(fb, cx - 5, cy + 5, cx - 9, cy + 9, INK, 3)


def eraser_icon(fb, cx, cy):
    draw_line(fb, cx - 10, cy + 10, cx - 1, cy + 10, METAL)
    draw_line(fb, cx - 4, cy + 4, cx + 1, cy - 1, (255, 160, 175), 9)
    draw_line(fb, cx + 3, cy - 3, cx + 6, cy - 6, (70, 110, 200), 9)


def line_icon(fb, cx, cy):
    draw_line(fb, cx - 8, cy + 6, cx + 8, cy - 6, INK)
    for x, y in [(cx - 8, cy + 6), (cx + 8, cy - 6)]:
        fill_circle(fb, x, y, 3, WHITE)
        draw_circle(fb, x, y, 3, SHAPE_LINE)


def rect_icon(fb, cx, cy):
    fill_rect(fb, cx - 10, cy - 7, cx + 10, cy + 7, SHAPE_FILL)
    draw_rect(fb, cx - 10, cy - 7, cx + 10, cy + 7, SHAPE_LINE, 3)


def circle_icon(fb, cx, cy):
    fill_circle(fb, cx, cy, 9, SHAPE_FILL)
    draw_circle(fb, cx, cy, 9, SHAPE_LINE, 3)


def polygon_icon(fb, cx, cy):
    points = [(cx - 10, cy - 1), (cx - 2, cy - 9), (cx + 10, cy - 5), (cx + 7, cy + 8), (cx - 6, cy + 8)]
    fill_polygon(fb, points, SHAPE_FILL)
    draw_polygon(fb, points, SHAPE_LINE, 3)


def arrowhead(fb, tip, base, half_width, color):
    # Triângulo com a ponta em tip e a base atravessada em base
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    length = max(abs(dx), abs(dy))
    sx, sy = round(-dy / length * half_width), round(dx / length * half_width)
    fill_polygon(fb, [tip, (base[0] + sx, base[1] + sy), (base[0] - sx, base[1] - sy)], color)


def move_icon(fb, cx, cy):
    draw_line(fb, cx - 8, cy, cx + 8, cy, INK)
    draw_line(fb, cx, cy - 8, cx, cy + 8, INK)
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        arrowhead(fb, (cx + 11 * dx, cy + 11 * dy), (cx + 6 * dx, cy + 6 * dy), 4, INK)


def select_icon(fb, cx, cy):
    draw_dashed_rect(fb, cx - 10, cy - 8, cx + 10, cy + 8, INK, 2)
    for x, y in [(cx - 10, cy - 8), (cx + 10, cy - 8), (cx + 10, cy + 8), (cx - 10, cy + 8)]:
        fill_rect(fb, x - 1, y - 1, x + 1, y + 1, SHAPE_LINE)


def bucket_icon(style):
    def icon(fb, cx, cy):
        # A alça é só a metade de cima de um círculo
        for x, y in circle_points(cx - 2, cy - 2, 7):
            if y <= cy - 2:
                fb.put_pixel(x, y, INK)
        fill_rect(fb, cx - 9, cy - 2, cx + 5, cy + 10, METAL)
        fill_rect(fb, cx - 9, cy - 2, cx + 5, cy + 2, style.color)
        draw_rect(fb, cx - 9, cy - 2, cx + 5, cy + 10, INK)
        draw_line(fb, cx + 6, cy - 1, cx + 8, cy + 3, style.color, 3)
        fill_circle(fb, cx + 9, cy + 8, 2, style.color)
        draw_circle(fb, cx + 9, cy + 8, 2, INK)
    return icon


def outline_icon(fb, cx, cy):
    fill_rect(fb, cx - 8, cy - 6, cx + 8, cy + 6, WHITE)
    draw_rect(fb, cx - 8, cy - 6, cx + 8, cy + 6, SHAPE_LINE, 3)


def filled_icon(fb, cx, cy):
    fill_rect(fb, cx - 8, cy - 6, cx + 8, cy + 6, SHAPE_LINE)


def rotate_icon(clockwise):
    def icon(fb, cx, cy):
        # Três quartos de um círculo, com a seta no topo apontando pro lado do giro
        side = 1 if clockwise else -1
        stamp(fb, [(x, y) for x, y in circle_points(cx, cy, 8) if not ((x - cx) * side > 0 and y < cy)], SHAPE_LINE, 3)
        arrowhead(fb, (cx + 4 * side, cy - 8), (cx - side, cy - 8), 4, SHAPE_LINE)
    return icon


def scale_icon(grow):
    def icon(fb, cx, cy):
        fill_rect(fb, cx - 10, cy + 1, cx - 2, cy + 9, SHAPE_FILL)
        draw_rect(fb, cx - 10, cy + 1, cx - 2, cy + 9, SHAPE_LINE)
        draw_dashed_rect(fb, cx - 10, cy - 9, cx + 10, cy + 9, SHAPE_LINE, 2)
        start, end = ((cx - 1, cy), (cx + 7, cy - 8)) if grow else ((cx + 7, cy - 8), (cx - 1, cy))
        draw_line(fb, *start, *end, INK)
        arrowhead(fb, end, (end[0] - (end[0] - start[0]) // 2, end[1] - (end[1] - start[1]) // 2), 3, INK)
    return icon


def apply_icon(fb, cx, cy):
    draw_line(fb, cx - 7, cy, cx - 2, cy + 5, GREEN, 3)
    draw_line(fb, cx - 2, cy + 5, cx + 8, cy - 6, GREEN, 3)


def delete_icon(fb, cx, cy):
    draw_line(fb, cx - 6, cy - 6, cx + 6, cy + 6, RED, 3)
    draw_line(fb, cx - 6, cy + 6, cx + 6, cy - 6, RED, 3)


def thickness_icon(size):
    def icon(fb, cx, cy):
        draw_line(fb, cx - 24, cy, cx + 24, cy, INK, size)
    return icon


def swatch_icon(color):
    def icon(fb, cx, cy):
        fill_rect(fb, cx - 11, cy - 7, cx + 11, cy + 7, color)
        draw_rect(fb, cx - 11, cy - 7, cx + 11, cy + 7, BORDER)
    return icon


def undo_icon(fb, cx, cy):
    # Uma seta que faz a curva e volta: reta em cima, meia volta à direita, reta embaixo
    stamp(fb, [(x, y) for x, y in circle_points(cx + 3, cy + 1, 5) if x >= cx + 3], SHAPE_LINE, 3)
    draw_line(fb, cx - 3, cy - 4, cx + 3, cy - 4, SHAPE_LINE, 3)
    draw_line(fb, cx - 4, cy + 6, cx + 3, cy + 6, SHAPE_LINE, 3)
    arrowhead(fb, (cx - 9, cy - 4), (cx - 4, cy - 4), 4, SHAPE_LINE)


def new_icon(fb, cx, cy):
    fill_rect(fb, cx - 8, cy - 5, cx + 5, cy + 8, WHITE)
    fill_rect(fb, cx - 8, cy - 10, cx - 1, cy - 5, WHITE)
    # A ponta dobrada é um triângulo: cada linha dele é um pouco mais larga que a de cima
    for i in range(6):
        fb.put_span(cx, cx + i, cy - 10 + i, (215, 218, 225))
    corners = [(cx - 8, cy - 10), (cx, cy - 10), (cx + 5, cy - 5), (cx + 5, cy + 8), (cx - 8, cy + 8)]
    for i in range(5):
        draw_line(fb, *corners[i], *corners[(i + 1) % 5], INK)
    draw_line(fb, cx, cy - 10, cx, cy - 5, INK)
    draw_line(fb, cx, cy - 5, cx + 5, cy - 5, INK)
    fill_circle(fb, cx + 6, cy + 6, 5, GREEN)
    draw_line(fb, cx + 4, cy + 6, cx + 8, cy + 6, WHITE)
    draw_line(fb, cx + 6, cy + 4, cx + 6, cy + 8, WHITE)


def save_icon(fb, cx, cy):
    fill_rect(fb, cx - 9, cy - 9, cx + 9, cy + 9, (60, 90, 160))
    fill_rect(fb, cx - 5, cy - 9, cx + 4, cy - 4, (200, 205, 215))
    fill_rect(fb, cx + 1, cy - 8, cx + 3, cy - 5, (60, 90, 160))
    fill_rect(fb, cx - 6, cy + 1, cx + 6, cy + 7, WHITE)
    draw_line(fb, cx - 4, cy + 3, cx + 4, cy + 3, METAL)
    draw_line(fb, cx - 4, cy + 5, cx + 4, cy + 5, METAL)


class Button:
    def __init__(self, x, y, w, h, label, icon, on_click, is_active, applies, why):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.label = label
        self.icon = icon
        self.on_click = on_click
        self.is_active = is_active
        self.applies = applies
        self.why = why

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
            "Linha": line_icon, "Retângulo": rect_icon, "Círculo": circle_icon, "Polígono": polygon_icon,
            "Balde": bucket_icon(app.style), "Selecionar": select_icon, "Mover": move_icon,
        }
        tool_why = lambda: f"sem efeito na ferramenta {app.tool.name}"
        # O t=t prende cada ferramenta no seu botão; sem isso, todos ficariam com a última do laço
        self.add_section(2, 30, [
            (f"{t.name} ({t.shortcut})", icons[t.name], lambda t=t: app.select_tool(t), lambda t=t: app.tool is t)
            for t in app.tools
        ])
        self.add_section(2, 26, [
            ("Vazado (V)", outline_icon, lambda: app.set_filled(False), lambda: not app.style.filled),
            ("Preenchido (V)", filled_icon, lambda: app.set_filled(True), lambda: app.style.filled),
        ], applies=lambda: app.tool.uses_fill, why=tool_why)
        self.add_section(1, 18, [
            (f"{name.capitalize()} ({i + 1})", thickness_icon(px),
             lambda n=name: app.set_size(n), lambda n=name: app.size_name == n)
            for i, (name, px) in enumerate(SIZES.items())
        ], applies=lambda: app.tool.uses_size, why=tool_why)
        self.add_section(2, 24, [
            (name, swatch_icon(c), lambda c=c: app.set_color(c), lambda c=c: app.style.color == c)
            for name, c in PALETTE
        ])
        self.add_section(2, 26, [
            ("Girar pra esquerda (Q)", rotate_icon(False), lambda: app.rotate_selection(-ROTATION_STEP), lambda: False),
            ("Girar pra direita (E)", rotate_icon(True), lambda: app.rotate_selection(ROTATION_STEP), lambda: False),
            ("Diminuir (-)", scale_icon(False), lambda: app.scale_selection(1 / SCALE_STEP), lambda: False),
            ("Aumentar (+)", scale_icon(True), lambda: app.scale_selection(SCALE_STEP), lambda: False),
            ("Fixar no desenho (Enter)", apply_icon, app.commit_selection, lambda: False),
            ("Apagar a forma (Delete)", delete_icon, app.delete_selection, lambda: False),
        ], applies=lambda: app.selection is not None, why=lambda: "desenhe uma forma ou selecione uma área primeiro")
        self.add_section(2, 28, [
            ("Novo (N)", new_icon, app.new_drawing, lambda: False),
            ("Salvar (S)", save_icon, app.save, lambda: False),
        ])
        self.add_section(2, 28, [
            ("Desfazer (Ctrl+Z)", undo_icon, app.undo, lambda: False),
        ], applies=lambda: bool(app.history) or app.selection is not None, why=lambda: "nada pra desfazer")

    def add_section(self, cols, h, items, applies=lambda: True, why=lambda: ""):
        w = (self.fb.width - 2 * MARGIN - GAP * (cols - 1)) // cols
        for i, (label, icon, on_click, is_active) in enumerate(items):
            x = MARGIN + (i % cols) * (w + GAP)
            y = self.y + (i // cols) * (h + GAP)
            self.buttons.append(Button(x, y, w, h, label, icon, on_click, is_active, applies, why))
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
