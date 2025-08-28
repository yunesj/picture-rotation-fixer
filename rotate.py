import argparse
import logging
import os
from multiprocessing import Pool, cpu_count

import cv2
from PIL import Image
from tqdm import tqdm


def detect_faces(image):
    """Return True if faces detected, else False"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
    return len(faces) > 0


def auto_rotate(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return

    for angle, rotate_code in [
        (0, None),
        (90, cv2.ROTATE_90_CLOCKWISE),
        (180, cv2.ROTATE_180),
        (270, cv2.ROTATE_90_COUNTERCLOCKWISE),
    ]:
        rotated = cv2.rotate(img, rotate_code) if rotate_code else img
        if detect_faces(rotated):
            # save back (overwrite)
            Image.fromarray(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)).save(image_path)
            logging.debug(f"✔ Rotated {image_path} to {angle}°")
            return

    logging.debug(f"⚠ No faces found in {image_path}, left as-is.")


def process_directory(root_dir):
    image_paths = []
    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                image_paths.append(os.path.join(root, f))

    with Pool(cpu_count()) as pool:
        list(
            tqdm(pool.imap_unordered(auto_rotate, image_paths), total=len(image_paths))
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Auto-rotate scanned photos using face detection."
    )
    parser.add_argument(
        "folder",
        type=str,
        nargs="?",
        default=os.path.expanduser("~/LocalFiles/Scanned/Photos"),
        help="Folder to process (default: ~/LocalFiles/Scanned/Photos)",
    )
    args = parser.parse_args()
    process_directory(args.folder)
