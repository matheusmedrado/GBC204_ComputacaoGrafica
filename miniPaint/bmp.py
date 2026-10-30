import struct


def save_bmp(fb, path):
    # Cada linha do arquivo precisa ocupar um múltiplo de 4 bytes
    row_size = (fb.width * 3 + 3) // 4 * 4
    padding = bytes(row_size - fb.width * 3)
    image_size = row_size * fb.height

    with open(path, "wb") as f:
        # Cabeçalho do arquivo (14 bytes) e da imagem (40 bytes): 24 bits por pixel, sem compressão
        f.write(b"BM" + struct.pack("<IHHI", 54 + image_size, 0, 0, 54))
        f.write(struct.pack("<IiiHHIIiiII", 40, fb.width, fb.height, 1, 24, 0, image_size, 2835, 2835, 0, 0))
        # O BMP guarda as linhas de baixo pra cima e cada cor na ordem azul, verde, vermelho
        for y in range(fb.height - 1, -1, -1):
            f.write(fb.pixels[y, :, ::-1].tobytes() + padding)
