import os.path
from brightfield_img_to_png import parallel_brightfield_to_png

BASE_DIR = "/home/safal/raavan/parasite/media/"

with open("../bright.txt") as f:
    brightfield_imgs = f.read()

brightfield_imgs = map(
    lambda x: os.path.join(BASE_DIR, x), brightfield_imgs.splitlines()
)
parallel_brightfield_to_png(brightfield_imgs)
