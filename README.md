# Image Stitching Scripts

This repository contains three Python scripts for image stitching using OpenCV. Each script offers different levels of functionality for combining multiple images into panoramic views.

## Prerequisites

- Python 3.x
- OpenCV (`cv2`)
- imutils
- numpy

Install dependencies:
```bash
pip install opencv-python imutils numpy
```

## Scripts Overview

### 1. `stitch_simple.py` - Basic Image Stitching

The simplest image stitching script that processes all images in a directory.

**Usage:**
```bash
python stitch_simple.py -i <input_directory> -o <output_image>
```

**Parameters:**
- `-i, --images` (required): Path to input directory containing images to stitch
- `-o, --output` (required): Path to the output panoramic image

**Example:**
```bash
python stitch_simple.py -i ./photos -o panorama.jpg
```

**Features:**
- Loads all images from the specified directory
- Uses OpenCV's built-in stitcher
- Provides detailed error messages for stitching failures
- Automatic detection of OpenCV version compatibility

### 2. `stitch_images.py` - Image Stitching with Cropping

Enhanced version with optional cropping functionality to remove black borders.

**Usage:**
```bash
python stitch_images.py -i <input_directory> -o <output_image> [-c <crop_flag>]
```

**Parameters:**
- `-i, --images` (required): Path to input directory containing images to stitch
- `-o, --output` (required): Path to the output panoramic image
- `-c, --crop` (optional): Whether to crop out largest rectangular region (0=no crop, 1=crop). Default: 0

**Examples:**
```bash
# Basic stitching without cropping
python stitch_images.py -i ./photos -o panorama.jpg

# Stitching with automatic cropping
python stitch_images.py -i ./photos -o panorama_cropped.jpg -c 1
```

**Features:**
- All features from `stitch_simple.py`
- Optional automatic cropping to remove black borders
- Intelligent rectangular region detection
- Border padding and erosion-based cropping algorithm

### 3. `stitch_sequence.py` - Sequential Image Stitching

Most advanced script with selective image processing capabilities.

**Usage:**
```bash
python stitch_sequence.py -i <input_directory> -o <output_image> [-c <crop_flag>] [-s <start_filename>] [-n <count>]
```

**Parameters:**
- `-i, --images` (required): Path to input directory containing images to stitch
- `-o, --output` (required): Path to the output panoramic image
- `-c, --crop` (optional): Whether to crop out largest rectangular region (0=no crop, 1=crop). Default: 0
- `-s, --start` (optional): Starting filename to begin processing from (e.g., "frame_0009.jpg")
- `-n, --count` (optional): Number of images to process from the starting point

**Examples:**
```bash
# Process all images (same as stitch_images.py)
python stitch_sequence.py -i ./photos -o panorama.jpg

# Process 10 images starting from a specific file
python stitch_sequence.py -i ./photos -o partial_panorama.jpg -s frame_0009.jpg -n 10

# Process specific sequence with cropping
python stitch_sequence.py -i ./photos -o cropped_sequence.jpg -s frame_0005.jpg -n 15 -c 1
```

**Features:**
- All features from previous scripts
- Selective image processing by specifying start file and count
- Useful for processing specific sequences from large image collections
- Maintains sorted order of images
- Error handling for missing start files

## Error Codes

All scripts provide detailed error messages for stitching failures:

- **Status 0**: Success
- **Status 1**: `ERR_NEED_MORE_IMGS` - Need more input images to construct panorama
- **Status 2**: `ERR_HOMOGRAPHY_EST_FAIL` - Homography estimation failed
- **Status 3**: `ERR_CAMERA_PARAMS_ADJUST_FAIL` - Camera parameter adjustment failed

## Tips for Best Results

1. **Image Quality**: Use high-quality images with sufficient overlap (30-50%)
2. **Consistent Lighting**: Images should have similar lighting conditions
3. **Stable Camera**: Avoid excessive camera shake or movement
4. **Sequential Order**: Images should be in sequential order for best results
5. **File Naming**: Use consistent naming patterns (e.g., frame_0001.jpg, frame_0002.jpg)

## Common Use Cases

- **`stitch_simple.py`**: Quick panoramic creation from a small set of images
- **`stitch_images.py`**: When you need clean panoramas without black borders
- **`stitch_sequence.py`**: Processing specific portions of large image sequences or video frames