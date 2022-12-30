import os.path
from brightfield_img_to_png import brightfield_img_to_png

BASE_DIR = "/home/safal/raavan/parasite/"
while True:
    media_url = input("404 Path: ")

    basename, ext = media_url.lstrip("/").rsplit(".", 1)

    file_path = os.path.join(BASE_DIR, f"{basename}.jpg")

    brightfield_img_to_png(file_path)
