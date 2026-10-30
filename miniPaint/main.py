import math
import time
from datetime import datetime
from pathlib import Path

import glfw
from OpenGL.GL import *

from bmp import save_bmp
from framebuffer import Framebuffer
from raster import draw_dashed_rect
from tools import (Brush, Bucket, CircleTool, Eraser, LineTool, MoveTool, Pencil, PolygonTool, RectTool,
                   Style)
from transform import around, rotation, scale, translation
from ui import ROTATION_STEP, SCALE_STEP, SIZES, TOOLBAR_WIDTH, Toolbar

CANVAS_WIDTH, CANVAS_HEIGHT = 800, 600
SIZE_KEYS = {glfw.KEY_1: "fino", glfw.KEY_2: "médio", glfw.KEY_3: "grosso"}
SAVE_DIR = Path(__file__).resolve().parent / "desenhos"
SELECTION_COLOR = (40, 100, 220)


class MiniPaint:
    def __init__(self):
        self.canvas = Framebuffer(CANVAS_WIDTH, CANVAS_HEIGHT)
        # A tela é o canvas mais a forma selecionada e a prévia do que ainda está sendo desenhado
        self.screen = Framebuffer(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.style = Style()
        # A última forma desenhada fica solta por cima do canvas até ser fixada
        self.selection = None
        self.set_size("médio")
        brush = Brush(self.style)
        self.tools = [Pencil(self.style), brush, Eraser(self.style), LineTool(self.style),
                      RectTool(self.style), CircleTool(self.style), PolygonTool(self.style),
                      Bucket(self.style), MoveTool(self)]
        self.tool_keys = {getattr(glfw, "KEY_" + t.shortcut): t for t in self.tools}
        self.tool = brush
        self.toolbar = Toolbar(self, TOOLBAR_WIDTH, CANVAS_HEIGHT)
        self.dragging = False
        self.mouse = (-1, -1)
        self.over_canvas = False
        self.message, self.message_until = "", 0
        self.title = None
        self.window = None

    def init_window(self):
        if not glfw.init():
            raise RuntimeError("Não deu pra iniciar o GLFW")

        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
        self.window = glfw.create_window(TOOLBAR_WIDTH + CANVAS_WIDTH, CANVAS_HEIGHT, "Mini Paint", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Não deu pra criar a janela")

        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self.on_cursor_move)
        glfw.set_cursor_enter_callback(self.window, self.on_cursor_enter)
        glfw.set_key_callback(self.window, self.on_key)
        self.crosshair = glfw.create_standard_cursor(glfw.CROSSHAIR_CURSOR)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    def select_tool(self, tool):
        if self.dragging:
            return
        self.tool.cancel()
        # Trocar de ferramenta fixa a forma, menos indo pro Mover, que existe justamente pra mexer nela
        if not tool.keeps_selection:
            self.commit_selection()
        self.tool = tool

    def set_color(self, color):
        self.style.color = color
        if self.selection:
            self.selection.style.color = color

    def set_size(self, name):
        self.size_name, self.style.size = name, SIZES[name]
        if self.selection:
            self.selection.style.size = SIZES[name]

    def set_filled(self, filled):
        self.style.filled = filled
        if self.selection:
            self.selection.style.filled = filled

    def select(self, shape):
        if shape:
            self.selection = shape

    def commit_selection(self):
        if self.selection:
            self.selection.draw(self.canvas)
            self.selection = None

    def delete_selection(self):
        self.selection = None

    def selection_box(self):
        if not self.selection:
            return None
        x0, y0, x1, y1 = self.selection.bounds()
        return x0 - 4, y0 - 4, x1 + 4, y1 + 4

    def move_selection(self, dx, dy):
        if self.selection:
            self.selection.transform(translation(dx, dy))

    def rotate_selection(self, degrees):
        if self.selection:
            self.selection.transform(around(self.selection.center(), rotation(math.radians(degrees))))

    def scale_selection(self, factor):
        if self.selection:
            self.selection.transform(around(self.selection.center(), scale(factor, factor)))

    def new_drawing(self):
        self.tool.cancel()
        self.selection = None
        self.canvas.clear()

    def save(self):
        self.commit_selection()
        SAVE_DIR.mkdir(exist_ok=True)
        path = SAVE_DIR / f"desenho-{datetime.now():%Y%m%d-%H%M%S}.bmp"
        save_bmp(self.canvas, path)
        self.message, self.message_until = f"Salvo em desenhos/{path.name}", time.time() + 3
        print(f"Desenho salvo em {path}")

    def to_canvas(self, x, y):
        return int(x) - TOOLBAR_WIDTH, int(y)

    def on_mouse_button(self, window, button, action, mods):
        if button != glfw.MOUSE_BUTTON_LEFT:
            return
        x, y = glfw.get_cursor_pos(window)
        if action == glfw.PRESS and x < TOOLBAR_WIDTH:
            self.toolbar.click(int(x), int(y))
        elif action == glfw.PRESS:
            if not self.tool.keeps_selection:
                self.commit_selection()
            self.dragging = True
            self.select(self.tool.press(self.canvas, *self.to_canvas(x, y)))
        elif action == glfw.RELEASE and self.dragging:
            self.dragging = False
            self.select(self.tool.release(self.canvas, *self.to_canvas(x, y)))

    def on_cursor_move(self, window, x, y):
        self.mouse = (int(x), int(y))
        over_canvas = x >= TOOLBAR_WIDTH
        if over_canvas != self.over_canvas:
            self.over_canvas = over_canvas
            glfw.set_cursor(window, self.crosshair if over_canvas else None)
        if self.dragging:
            self.tool.drag(self.canvas, *self.to_canvas(x, y))
        else:
            self.tool.hover(*self.to_canvas(x, y))

    def on_cursor_enter(self, window, entered):
        if not entered:
            self.mouse = (-1, -1)

    def on_key(self, window, key, scancode, action, mods):
        if action == glfw.RELEASE:
            return
        step = 1 if mods & glfw.MOD_SHIFT else 5
        moves = {glfw.KEY_LEFT: (-step, 0), glfw.KEY_RIGHT: (step, 0), glfw.KEY_UP: (0, -step), glfw.KEY_DOWN: (0, step)}

        # As transformações seguem enquanto a tecla está apertada; o resto só vale no primeiro toque
        if key in moves:
            self.move_selection(*moves[key])
        elif key == glfw.KEY_Q:
            self.rotate_selection(-ROTATION_STEP)
        elif key == glfw.KEY_E:
            self.rotate_selection(ROTATION_STEP)
        elif key in (glfw.KEY_EQUAL, glfw.KEY_KP_ADD):
            self.scale_selection(SCALE_STEP)
        elif key in (glfw.KEY_MINUS, glfw.KEY_KP_SUBTRACT):
            self.scale_selection(1 / SCALE_STEP)
        elif action != glfw.PRESS:
            return
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key in (glfw.KEY_ENTER, glfw.KEY_KP_ENTER):
            shape = self.tool.enter()
            if shape:
                self.select(shape)
            else:
                self.commit_selection()
        elif key in (glfw.KEY_DELETE, glfw.KEY_BACKSPACE):
            self.delete_selection()
        elif key == glfw.KEY_N:
            self.new_drawing()
        elif key == glfw.KEY_S:
            self.save()
        elif key == glfw.KEY_V:
            self.set_filled(not self.style.filled)
        elif key in SIZE_KEYS:
            self.set_size(SIZE_KEYS[key])
        elif key in self.tool_keys:
            self.select_tool(self.tool_keys[key])

    def update_title(self):
        hovered = self.toolbar.button_at(*self.mouse)
        if time.time() < self.message_until:
            text = self.message
        elif hovered and not hovered.applies():
            text = f"{hovered.label}  |  {hovered.why()}"
        elif hovered:
            text = hovered.label
        elif self.selection:
            text = "Forma selecionada  |  arraste com Mover ou use as setas, Q e E giram, + e - mudam o tamanho, Enter fixa"
        else:
            fill = "preenchido" if self.style.filled else "vazado"
            text = f"{self.tool.name}  |  {self.size_name}  |  {fill}"
        if text != self.title:
            self.title = text
            glfw.set_window_title(self.window, f"Mini Paint  |  {text}")

    def show(self, fb, x, y):
        window_width, window_height = glfw.get_window_size(self.window)
        # No Mac, cada ponto da janela pode ter 2x2 pixels de verdade
        scale = glfw.get_framebuffer_size(self.window)[0] / window_width

        # O OpenGL monta a imagem de baixo pra cima, então começamos no topo e descemos
        glWindowPos2i(int(x * scale), int((window_height - y) * scale))
        glPixelZoom(scale, -scale)
        glDrawPixels(fb.width, fb.height, GL_RGB, GL_UNSIGNED_BYTE, fb.pixels)

    def render(self):
        self.screen.copy_from(self.canvas)
        if self.selection:
            self.selection.draw(self.screen)
            draw_dashed_rect(self.screen, *self.selection_box(), SELECTION_COLOR)
        self.tool.preview(self.screen)
        self.toolbar.draw(self.mouse)
        glClear(GL_COLOR_BUFFER_BIT)
        self.show(self.toolbar.fb, 0, 0)
        self.show(self.screen, TOOLBAR_WIDTH, 0)

    def run(self):
        self.init_window()
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.render()
            self.update_title()
            glfw.swap_buffers(self.window)
        glfw.terminate()


if __name__ == "__main__":
    MiniPaint().run()
