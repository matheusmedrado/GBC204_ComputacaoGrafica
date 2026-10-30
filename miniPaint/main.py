import glfw
from OpenGL.GL import *

from framebuffer import Framebuffer
from tools import Brush, Eraser, Line, Pencil, Style

WIDTH, HEIGHT = 800, 600
SIZES = {glfw.KEY_1: ("fino", 1), glfw.KEY_2: ("médio", 5), glfw.KEY_3: ("grosso", 11)}


class MiniPaint:
    def __init__(self):
        self.canvas = Framebuffer(WIDTH, HEIGHT)
        # A tela é o canvas mais a prévia do que ainda está sendo desenhado
        self.screen = Framebuffer(WIDTH, HEIGHT)
        self.style = Style()
        self.size_name = "fino"
        self.tools = {
            glfw.KEY_P: Pencil(self.style),
            glfw.KEY_I: Brush(self.style),
            glfw.KEY_B: Eraser(self.style),
            glfw.KEY_L: Line(self.style),
        }
        self.tool = self.tools[glfw.KEY_P]
        self.dragging = False
        self.window = None

    def init_window(self):
        if not glfw.init():
            raise RuntimeError("Não deu pra iniciar o GLFW")

        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
        self.window = glfw.create_window(WIDTH, HEIGHT, "Mini Paint", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Não deu pra criar a janela")

        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self.on_cursor_move)
        glfw.set_key_callback(self.window, self.on_key)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        self.update_title()

    def update_title(self):
        glfw.set_window_title(self.window, f"Mini Paint  |  {self.tool.name}  |  {self.size_name}")

    def on_mouse_button(self, window, button, action, mods):
        if button != glfw.MOUSE_BUTTON_LEFT:
            return
        x, y = glfw.get_cursor_pos(window)
        if action == glfw.PRESS:
            self.dragging = True
            self.tool.press(self.canvas, int(x), int(y))
        elif action == glfw.RELEASE and self.dragging:
            self.dragging = False
            self.tool.release(self.canvas, int(x), int(y))

    def on_cursor_move(self, window, x, y):
        if self.dragging:
            self.tool.drag(self.canvas, int(x), int(y))

    def on_key(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_N:
            self.canvas.clear()
        elif key in SIZES:
            self.size_name, self.style.size = SIZES[key]
        elif key in self.tools and not self.dragging:
            self.tool = self.tools[key]
        self.update_title()

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
        glClear(GL_COLOR_BUFFER_BIT)
        self.show(self.screen, 0, 0)

    def run(self):
        self.init_window()
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.render()
            glfw.swap_buffers(self.window)
        glfw.terminate()


if __name__ == "__main__":
    MiniPaint().run()
