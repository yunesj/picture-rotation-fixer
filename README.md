# Auto Rotate Scanned Photos

This Python script automatically rotates scanned family photos to the correct orientation using face detection.
It checks each image at 0°, 90°, 180°, 270° and keeps the first orientation where a face is detected upright.

⸻

## Features

• Recursively scans all subfolders.
• Supports .png, .jpg, .jpeg images.
• Uses OpenCV’s built-in Haar cascade face detector (fast & lightweight).
• Overwrites images in place (optional: can be changed to save in a separate folder).
• Parallel processing with progress bar using multiprocessing and tqdm.
• Available as a standalone binary, Homebrew formula, or Python script.

⸻

## Installation

### 1. Homebrew (Recommended for Mac users)

```sh
brew tap JustinGuese/homebrew-picture-rotation-fixer
brew install picture-rotation-fixer
```

### 2. Standalone Binary

Download the latest release from [GitHub Releases](https://github.com/JustinGuese/picture-rotation-fixer/releases).

- **Linux/Mac**: Download `picture-rotation-fixer` and make it executable:
  ```sh
  chmod +x picture-rotation-fixer
  ```
- **Windows**: Download `picture-rotation-fixer.exe`.

No Python installation required!

### 3. Python Package

1. Clone or download the repository.
2. Install dependencies:
   ```sh
   pip install opencv-python pillow tqdm
   ```
   Or using uv (recommended):
   ```sh
   uv install
   ```
3. (Optional) Install as a CLI tool:
   ```sh
   pip install .
   ```
   This adds the `picture-rotation-fixer` command to your PATH.

⸻

## Usage

### 1. Homebrew

```sh
picture-rotation-fixer /path/to/your/photos
```

### 2. Standalone Binary

- **Linux/Mac**:
  ```sh
  ./picture-rotation-fixer /path/to/your/photos
  ```
- **Windows**:
  ```cmd
  picture-rotation-fixer.exe C:\path\to\your\photos
  ```

### 3. Python

If installed as a package:

```sh
picture-rotation-fixer /path/to/your/photos
```

Or run the script directly:

```sh
python rotate.py /path/to/your/photos
```

If no folder is provided, it defaults to `~/LocalFiles/Scanned/Photos`.

⸻

## Requirements

• For Python usage: Python 3.12+
• OpenCV
• Pillow
• tqdm

⸻

## Example Output

✔ Rotated /Users/jguese/LocalFiles/Scanned/Photos/Album_1994/photo1.png to 180°
✔ Rotated /Users/jguese/LocalFiles/Scanned/Photos/Album_2001/photo2.png to 90°
⚠ No faces found in /Users/jguese/LocalFiles/Scanned/Photos/Album_1972/photo3.png, left as-is.

⸻

## Notes

• Best for portrait photos with faces.
• If no faces are found, the image is left untouched.
• If you want to keep originals, modify the script to save to a Rotated/ folder instead of overwriting.
• The script uses multiprocessing for parallel processing on multi-core systems.
