import time
from datetime import datetime
from pathlib import Path

import glfw
from OpenGL.GL import *

from bmp import save_bmp
from framebuffer import Framebuffer
from tools import Brush, Bucket, Circle, Eraser, Line, Pencil, Rect, Style
from ui import SIZES, TOOLBAR_WIDTH, Toolbar

CANVAS_WIDTH, CANVAS_HEIGHT = 800, 600
SIZE_KEYS = {glfw.KEY_1: "fino", glfw.KEY_2: "médio", glfw.KEY_3: "grosso"}
SAVE_DIR = Path(__file__).resolve().parent / "desenhos"


class MiniPaint:
    def __init__(self):
        self.canvas = Framebuffer(CANVAS_WIDTH, CANVAS_HEIGHT)
        # A tela é o canvas mais a prévia do que ainda está sendo desenhado
        self.screen = Framebuffer(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.style = Style()
        self.size_name = "fino"
        self.tools = [Pencil(self.style), Brush(self.style), Eraser(self.style), Line(self.style),
                      Rect(self.style), Circle(self.style), Bucket(self.style)]
        self.tool_keys = {getattr(glfw, "KEY_" + t.shortcut): t for t in self.tools}
        self.tool = self.tools[0]
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
        if not self.dragging:
            self.tool = tool

    def set_color(self, color):
        self.style.color = color

    def set_size(self, name):
        self.size_name, self.style.size = name, SIZES[name]

    def set_filled(self, filled):
        self.style.filled = filled

    def new_drawing(self):
        self.canvas.clear()

    def save(self):
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
            self.dragging = True
            self.tool.press(self.canvas, *self.to_canvas(x, y))
        elif action == glfw.RELEASE and self.dragging:
            self.dragging = False
            self.tool.release(self.canvas, *self.to_canvas(x, y))

    def on_cursor_move(self, window, x, y):
        self.mouse = (int(x), int(y))
        over_canvas = x >= TOOLBAR_WIDTH
        if over_canvas != self.over_canvas:
            self.over_canvas = over_canvas
            glfw.set_cursor(window, self.crosshair if over_canvas else None)
        if self.dragging:
            self.tool.drag(self.canvas, *self.to_canvas(x, y))

    def on_cursor_enter(self, window, entered):
        if not entered:
            self.mouse = (-1, -1)

    def on_key(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
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
        elif hovered:
            text = hovered.label
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
