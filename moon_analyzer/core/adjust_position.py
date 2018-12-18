def adjust_position(x, y, threshold_image, radius=5):
    width, height = threshold_image.size

    for i in range(x - radius, x + radius):
        for j in range(y - radius, y + radius):
            if 0 < i < width and 0 < j < height:
                if is_border(i, j, threshold_image):
                    return i, j
    return x, y


def is_border(x, y, threshold_image):
    width, height = threshold_image.size

    black_count, white_count = 0, 0

    for i in range(x - 1, x + 1):
        for j in range(y - 1, y + 1):
            if 0 < i < width and 0 < j < height:
                if threshold_image.getpixel((i, j)) == 255:
                    white_count += 1
                else:
                    black_count += 1

    return 4 > black_count >= white_count > 0
