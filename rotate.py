import argparse
import logging
import os
import sys
import warnings
from multiprocessing import Pool, cpu_count

import cv2
from PIL import Image
from tqdm import tqdm
from ultralytics import YOLO

# Suppress ultralytics warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning, module="ultralytics")


def get_model_path():
    """Get the path to the YOLO model, handling PyInstaller bundled resources"""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        bundle_dir = sys._MEIPASS
        model_path = os.path.join(bundle_dir, "ultralytics", "weights", "yolo11n.pt")
        if os.path.exists(model_path):
            return model_path

    # Default model name (will be downloaded if not present)
    return "yolo11n.pt"


def detect_faces(image):
    """Return True if faces detected, else False"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
    return len(faces) > 0


def detect_objects_yolo(image, model, confidence_threshold=0.5):
    """
    Detect objects using YOLOv8 model and return True if any objects detected.

    Args:
        image: OpenCV image array
        model: YOLO model instance
        confidence_threshold: Minimum confidence for detection

    Returns:
        bool: True if objects detected with sufficient confidence
    """
    try:
        # Run inference
        results = model(image, verbose=False)

        # Check if any detections meet confidence threshold
        for result in results:
            if hasattr(result, "boxes") and result.boxes is not None:
                confidences = result.boxes.conf.cpu().numpy()
                if len(confidences) > 0 and max(confidences) >= confidence_threshold:
                    return True
            # For OBB models, check oriented bounding boxes
            elif hasattr(result, "obb") and result.obb is not None:
                confidences = result.obb.conf.cpu().numpy()
                if len(confidences) > 0 and max(confidences) >= confidence_threshold:
                    return True
        return False
    except Exception as e:
        logging.debug(f"YOLO detection failed: {e}")
        return False


def auto_rotate(image_path):
    """
    Auto-rotate image based on detected features.

    First tries face detection, if no faces found, tries object detection.

    Args:
        image_path: Path to the image file
    """
    img = cv2.imread(image_path)
    if img is None:
        logging.debug(f"Could not load image: {image_path}")
        return

    for angle, rotate_code in [
        (0, None),
        (90, cv2.ROTATE_90_CLOCKWISE),
        (180, cv2.ROTATE_180),
        (270, cv2.ROTATE_90_COUNTERCLOCKWISE),
    ]:
        rotated = cv2.rotate(img, rotate_code) if rotate_code else img

        # First try face detection
        if detect_faces(rotated):
            # Save back (overwrite)
            Image.fromarray(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)).save(image_path)
            logging.debug(f"✔ Rotated {image_path} to {angle}° (faces detected)")
            return

    # If no faces found at any angle, try object detection as fallback
    try:
        model = YOLO(get_model_path())  # Use bundled or default model
        for angle, rotate_code in [
            (0, None),
            (90, cv2.ROTATE_90_CLOCKWISE),
            (180, cv2.ROTATE_180),
            (270, cv2.ROTATE_90_COUNTERCLOCKWISE),
        ]:
            rotated = cv2.rotate(img, rotate_code) if rotate_code else img

            if detect_objects_yolo(rotated, model, 0.5):  # Use default confidence
                # Save back (overwrite)
                Image.fromarray(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)).save(
                    image_path
                )
                logging.debug(f"✔ Rotated {image_path} to {angle}° (objects detected)")
                return
    except Exception as e:
        logging.debug(f"Failed to load YOLO model: {e}")

    logging.debug(f"⚠ No faces or objects found in {image_path}, left as-is.")


def process_single_image(image_path):
    """Helper function for multiprocessing"""
    auto_rotate(image_path)


def process_directory(root_dir):
    """
    Process all images in directory using cascading detection:
    1. Try face detection first
    2. If no faces found, try object detection
    3. If neither found, leave image unchanged

    Args:
        root_dir: Directory to process
    """
    # Find all image files
    image_paths = []
    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                image_paths.append(os.path.join(root, f))

    if not image_paths:
        print(f"No images found in {root_dir}")
        return

    print(f"Found {len(image_paths)} images")
    print("Detection strategy: Face detection first, object detection as fallback")

    # Process images with multiprocessing
    with Pool(cpu_count(), initializer=init_worker) as pool:
        list(
            tqdm(
                pool.imap_unordered(process_single_image, image_paths),
                total=len(image_paths),
                desc="Processing images",
            )
        )

    print("Processing complete!")

def init_worker():
    logging.basicConfig(
        level=logging.DEBUG,
        format=f"[%(processName)s] %(levelname)s: %(message)s",
        force=True
    )

if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()

    parser = argparse.ArgumentParser(
        description="Auto-rotate scanned photos using intelligent detection: face detection first, object detection as fallback.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (face detection first, object detection fallback)
  python rotate.py ~/Photos
  
  # Enable verbose logging to see what's being detected
  python rotate.py ~/Photos --verbose
        """,
    )

    parser.add_argument(
        "folder",
        type=str,
        nargs="?",
        default=os.path.expanduser("~/LocalFiles/Scanned/Photos"),
        help="Folder to process (default: ~/LocalFiles/Scanned/Photos)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(message)s")

    try:
        process_directory(args.folder)
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
