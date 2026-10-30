import math

# Mesma convenção dos slides: o ponto é a linha [x y 1] e vem antes da matriz, [x' y' 1] = [x y 1] · M


def translation(dx, dy):
    return [[1, 0, 0],
            [0, 1, 0],
            [dx, dy, 1]]


def scale(sx, sy):
    return [[sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]]


def rotation(angle):
    # O slide 15 escreve essa matriz pro ponto em coluna; com o ponto em linha ela vai transposta
    c, s = math.cos(angle), math.sin(angle)
    return [[c, s, 0],
            [-s, c, 0],
            [0, 0, 1]]


def multiply(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def around(center, m):
    # Leva o centro pra origem, aplica a transformação e devolve pro lugar
    cx, cy = center
    return multiply(multiply(translation(-cx, -cy), m), translation(cx, cy))


def apply(m, points):
    return [(x * m[0][0] + y * m[1][0] + m[2][0],
             x * m[0][1] + y * m[1][1] + m[2][1]) for x, y in points]
