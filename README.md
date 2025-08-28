# 📸 picture-rotation-fixer

## ✨ Features

- 🎯 **Intelligent Detection**: Cascading approach for maximum compatibility
  - 👤 **Face Detection First**: Uses OpenCV's Haar cascade for fast face detection
  - 🎨 **Object Detection Fallback**: Uses YOLOv8 for general object detection when no faces found
- 🔍 Recursively scans all subfolders
- 🖼️ Supports `.png`, `.jpg`, `.jpeg` images
- ⚡ Fast & lightweight with smart fallbacks
- 📝 Overwrites images in place _(preserves original if no rotation needed)_
- 🚀 Parallel processing with progress bar (`multiprocessing` + `tqdm`)
- 📦 Available as:
  - Homebrew formula (macOS)
  - Standalone binary (Linux/Mac/Windows)
  - Python script / packagened Photos

[![Build and Release Binaries](https://github.com/JustinGuese/picture-rotation-fixer/actions/workflows/build-and-release.yaml/badge.svg)](https://github.com/JustinGuese/picture-rotation-fixer/actions/workflows/build-and-release.yaml)

This tool automatically rotates scanned family photos to the correct orientation using **intelligent detection**.  
It uses a cascading approach: first tries **face detection**, then falls back to **object detection** if no faces are found.  
For each image, it evaluates orientations at `0°`, `90°`, `180°`, and `270°`, then saves the first orientation where content is detected upright.

---

## ✨ Features

- 🔍 Recursively scans all subfolders
- 🖼️ Supports `.png`, `.jpg`, `.jpeg` images
- ⚡ Uses OpenCV’s built-in Haar cascade face detector (fast & lightweight)
- 📝 Overwrites images in place _(can be configured to save to a separate folder)_
- 🚀 Parallel processing with a progress bar (`multiprocessing` + `tqdm`)
- 📦 Available as:
  - Homebrew formula (macOS)
  - Standalone binary (Linux/Mac/Windows)
  - Python script / package

---

## 📥 Installation

### 1. Homebrew (Recommended for macOS)

```sh
brew tap JustinGuese/homebrew-picture-rotation-fixer
brew install picture-rotation-fixer
```

---

### 2. Standalone Binary

Download the latest release from GitHub Releases.

**Linux / macOS:**

```sh
chmod +x picture-rotation-fixer
./picture-rotation-fixer /path/to/photos
```

**Windows:**

```sh
picture-rotation-fixer.exe C:\path\to\photos
```

_No Python installation required!_

---

### 3. Python Package

1. Clone or download the repository
2. Install dependencies:

   ```sh
   pip install opencv-python pillow tqdm ultralytics
   ```

   Or with uv (recommended):

   ```sh
   uv install
   ```

3. (Optional) Install as a CLI tool:

   ```sh
   pip install .
   ```

   This adds the `picture-rotation-fixer` command to your PATH.

---

## ▶️ Usage

**Homebrew / Installed CLI:**

```sh
picture-rotation-fixer /path/to/your/photos
```

**Standalone Binary:**

- Linux / macOS:

  ```sh
  ./picture-rotation-fixer /path/to/your/photos
  ```

- Windows:

  ```sh
  picture-rotation-fixer.exe C:\path\to\your\photos
  ```

**Python Script:**

```sh
python rotate.py /path/to/your/photos
```

If no folder is provided, it defaults to:  
`~/LocalFiles/Scanned/Photos`

---

## 📦 Requirements

- Python 3.12+ (only for Python usage)
- OpenCV (face detection)
- Pillow (image processing)
- tqdm (progress bars)
- ultralytics (YOLOv8 object detection)

---

## 🖥️ Example Output

```
✔ Rotated /Users/jguese/LocalFiles/Scanned/Photos/Album_1994/photo1.png to 180°
✔ Rotated /Users/jguese/LocalFiles/Scanned/Photos/Album_2001/photo2.png to 90°
⚠ No faces found in /Users/jguese/LocalFiles/Scanned/Photos/Album_1972/photo3.png, left as-is.
```

---

## 📝 Notes

- ✅ Best suited for portrait photos with visible faces
- ⚠ If no faces are detected, the image is left untouched
- 💾 To keep originals, configure the script to save to a `Rotated/` folder instead of overwriting
- 🧵 Uses multiprocessing for parallel batch processing on multi-core systems
