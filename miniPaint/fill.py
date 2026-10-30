def flood_fill(fb, x, y, color):
    target = fb.get_pixel(x, y)
    if target is None or target == color:
        return

    # Só os quatro vizinhos retos: com as diagonais, a tinta vazaria pelas linhas finas
    stack = [(x, y)]
    while stack:
        x, y = stack.pop()
        # Fora da tela o get_pixel devolve None, então a borda também segura a tinta
        if fb.get_pixel(x, y) != target:
            continue
        fb.put_pixel(x, y, color)
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
