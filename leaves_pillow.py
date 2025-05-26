import random
from time import time

from PIL import Image, ImageDraw


def dead_leaves(width, n_disks=10000, alpha=3.0, r_min=4, r_max=2000):
    img = Image.new("RGB", (width, width), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    vamin = 1/(r_max**(alpha-1))
    vamax = 1/(r_min**(alpha-1))

    for i in range(n_disks):
        r = vamin + (vamax - vamin) * random.random()
        r = int(1/(r**(1./(alpha-1))))
        x = random.randint(0, width-1)
        y = random.randint(0, width-1)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        draw.circle((x, y), r, fill=color, outline=False, width=0)
    return img


if __name__ == '__main__':
    start_time = time()

    for k in range(100):
        img = dead_leaves(width=1000)
        img.save(f"{k:03d}.png")

    print(time() - start_time)
