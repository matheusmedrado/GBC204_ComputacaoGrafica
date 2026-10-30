def bresenham_line(x0, y0, x1, y1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x1 >= x0 else -1
    sy = 1 if y1 >= y0 else -1

    # O slide mostra só o caso em que o x varia mais; aqui o eixo que varia mais faz esse papel
    if dx >= dy:
        main_step, side_step, long, short = (sx, 0), (0, sy), dx, dy
    else:
        main_step, side_step, long, short = (0, sy), (sx, 0), dy, dx

    x, y = x0, y0
    p = 2 * short - long
    points = [(x, y)]
    for _ in range(long):
        x += main_step[0]
        y += main_step[1]
        if p >= 0:
            x += side_step[0]
            y += side_step[1]
            p -= 2 * long
        p += 2 * short
        points.append((x, y))
    return points


def brush_offsets(size):
    # Os pixels de um disco: tudo que fica a até r de distância do centro
    r = size // 2
    return [(dx, dy)
            for dy in range(-r, r + 1)
            for dx in range(-r, r + 1)
            if dx * dx + dy * dy <= r * r]


def draw_line(fb, x0, y0, x1, y1, color, size=1):
    offsets = brush_offsets(size)
    for x, y in bresenham_line(x0, y0, x1, y1):
        for dx, dy in offsets:
            fb.put_pixel(x + dx, y + dy, color)
