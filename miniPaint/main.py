import glfw
from OpenGL.GL import *

from framebuffer import Framebuffer

WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)


class MiniPaint:
    def __init__(self):
        self.canvas = Framebuffer(WIDTH, HEIGHT)
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
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            x, y = glfw.get_cursor_pos(window)
            self.canvas.put_pixel(int(x), int(y), BLACK)

    def show(self, fb, x, y):
        window_width, window_height = glfw.get_window_size(self.window)
        # No Mac, cada ponto da janela pode ter 2x2 pixels de verdade
        scale = glfw.get_framebuffer_size(self.window)[0] / window_width

        # O OpenGL monta a imagem de baixo pra cima, então começamos no topo e descemos
        glWindowPos2i(int(x * scale), int((window_height - y) * scale))
        glPixelZoom(scale, -scale)
        glDrawPixels(fb.width, fb.height, GL_RGB, GL_UNSIGNED_BYTE, fb.pixels)

    def run(self):
        self.init_window()
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            glClear(GL_COLOR_BUFFER_BIT)
            self.show(self.canvas, 0, 0)
            glfw.swap_buffers(self.window)
        glfw.terminate()


if __name__ == "__main__":
    MiniPaint().run()
