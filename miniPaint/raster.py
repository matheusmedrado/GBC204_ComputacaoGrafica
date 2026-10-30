import math


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


def circle_octant(r):
    # Só um oitavo do círculo; os outros sete pedaços saem espelhando esse
    x, y, d = 0, r, 1 - r
    points = [(x, y)]
    while y > x:
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
        points.append((x, y))
    return points


def circle_points(cx, cy, r):
    points = []
    for x, y in circle_octant(r):
        points += [(cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y), (cx - x, cy - y),
                   (cx + y, cy + x), (cx - y, cy + x), (cx + y, cy - x), (cx - y, cy - x)]
    return points


def brush_offsets(size):
    # Os pixels de um disco: tudo que fica a até r de distância do centro
    r = size // 2
    return [(dx, dy)
            for dy in range(-r, r + 1)
            for dx in range(-r, r + 1)
            if dx * dx + dy * dy <= r * r]


def stamp(fb, points, color, size):
    offsets = brush_offsets(size)
    for x, y in points:
        for dx, dy in offsets:
            fb.put_pixel(x + dx, y + dy, color)


def draw_line(fb, x0, y0, x1, y1, color, size=1):
    stamp(fb, bresenham_line(x0, y0, x1, y1), color, size)


def draw_polygon(fb, points, color, size=1):
    for i in range(len(points)):
        draw_line(fb, *points[i], *points[(i + 1) % len(points)], color, size)


def fill_polygon(fb, points, color):
    # Varre a figura linha por linha: acha onde cada aresta cruza aquela altura e pinta entre os pares de cruzamentos
    ys = [y for _, y in points]
    for y in range(min(ys), max(ys) + 1):
        crossings = []
        for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
            # Cada aresta conta a ponta de cima e não a de baixo, pra um vértice não valer por dois
            if min(y0, y1) <= y < max(y0, y1):
                crossings.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        crossings.sort()
        for a, b in zip(crossings[::2], crossings[1::2]):
            # Cruzamentos muito juntos podem não ter nenhum pixel entre eles
            if math.ceil(a) <= math.floor(b):
                fb.put_span(math.ceil(a), math.floor(b), y, color)
    draw_polygon(fb, points, color)


def draw_rect(fb, x0, y0, x1, y1, color, size=1):
    draw_polygon(fb, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, size)


def draw_dashed_rect(fb, x0, y0, x1, y1, color, dash=4):
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for i in range(4):
        for k, (x, y) in enumerate(bresenham_line(*corners[i], *corners[(i + 1) % 4])):
            if k // dash % 2 == 0:
                fb.put_pixel(x, y, color)


def fill_rect(fb, x0, y0, x1, y1, color):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        fb.put_span(x0, x1, y, color)


def blend_rect(fb, x0, y0, x1, y1, color, t):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        fb.blend_span(x0, x1, y, color, t)


def draw_circle(fb, cx, cy, r, color, size=1):
    stamp(fb, circle_points(cx, cy, r), color, size)


def fill_circle(fb, cx, cy, r, color):
    # Cada ponto do oitavo dá as pontas de quatro trechos horizontais, um em cima e outro embaixo do centro
    for x, y in circle_octant(r):
        fb.put_span(cx - x, cx + x, cy + y, color)
        fb.put_span(cx - x, cx + x, cy - y, color)
        fb.put_span(cx - y, cx + y, cy + x, color)
        fb.put_span(cx - y, cx + y, cy - x, color)
