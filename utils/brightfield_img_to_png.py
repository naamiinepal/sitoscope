"""
This script converts the brightfield images captured
and saved in the .tiff format to .png format.
"""
import argparse
import os
from glob import glob
import time

import cv2

import concurrent.futures


def brightfield_img_to_png(brightfield_img_path: str):
    print("Working on:", brightfield_img_path)

    # Read the brightfield image
    img = cv2.imread(brightfield_img_path)

    # Convert the image to .png format
    cv2.imwrite(
        brightfield_img_path.rsplit(".", 1)[0] + ".png",
        img,
        [cv2.IMWRITE_PNG_COMPRESSION, 9],
    )
    os.remove(brightfield_img_path)


def main(args):
    brightfield_img_path = args.brightfield_img_path

    # Get the list of brightfield images
    brightfield_imgs = glob(f"{brightfield_img_path}/**/*_B.jpg", recursive=True)

    start = time.time()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(brightfield_img_to_png, brightfield_imgs)

    print("\n\nElapsed time:", time.time() - start, end="\n\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--brightfield_img_path", type=str, required=True)
    args = parser.parse_args()
    main(args)
