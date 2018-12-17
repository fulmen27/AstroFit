def threshold_image(pil_image, threshold=128):
    gray = pil_image.convert('L')
    return gray.point(lambda x: 0 if x < threshold else 255, "1")
