from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
import os
import glob

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", type=str, required=True,
    help="path to input directory of images to stitch")
ap.add_argument("-o", "--output", type=str, required=True,
    help="path to the output image")
ap.add_argument("-c", "--crop", type=int, default=0,
    help="whether to crop out largest rectangular region")
ap.add_argument("-s", "--start", type=str, default=None,
    help="starting filename (e.g., frame_0009.jpg)")
ap.add_argument("-n", "--count", type=int, default=None,
    help="number of images to process from start")
args = vars(ap.parse_args())

print("[INFO] loading images...")

if args["start"] is not None and args["count"] is not None:
    # Extract the pattern from the start filename
    start_file = args["start"]
    base_dir = args["images"]
    
    # Find the starting file
    start_path = os.path.join(base_dir, start_file)
    if not os.path.exists(start_path):
        print(f"[ERROR] Starting file {start_file} not found in {base_dir}")
        exit(1)
    
    # Get all image files and sort them
    all_images = sorted(list(paths.list_images(base_dir)))
    
    # Find the index of the starting file
    start_index = None
    for i, img_path in enumerate(all_images):
        if os.path.basename(img_path) == start_file:
            start_index = i
            break
    
    if start_index is None:
        print(f"[ERROR] Could not find {start_file} in the image list")
        exit(1)
    
    # Select the sequence of images
    end_index = min(start_index + args["count"], len(all_images))
    selected_images = all_images[start_index:end_index]
    
    print(f"[INFO] Processing {len(selected_images)} images starting from {start_file}")
    imagePaths = selected_images
    
else:
    # Original behavior - process all images
    imagePaths = sorted(list(paths.list_images(args["images"])))
    print(f"[INFO] Processing all {len(imagePaths)} images in directory")

images = []
for imagePath in imagePaths:
    image = cv2.imread(imagePath)
    images.append(image)
    print(f"[INFO] loaded {os.path.basename(imagePath)}")

print("[INFO] stitching images...")
stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
(status, stitched) = stitcher.stitch(images)

if status == 0:
    if args["crop"] > 0:
        print("[INFO] cropping...")
        stitched = cv2.copyMakeBorder(stitched, 10, 10, 10, 10,
            cv2.BORDER_CONSTANT, (0, 0, 0))

        gray = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)

        mask = np.zeros(thresh.shape, dtype="uint8")
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

        minRect = mask.copy()
        sub = mask.copy()

        while cv2.countNonZero(sub) > 0:
            minRect = cv2.erode(minRect, None)
            sub = cv2.subtract(minRect, thresh)

        cnts = cv2.findContours(minRect.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)
        (x, y, w, h) = cv2.boundingRect(c)

        stitched = stitched[y:y + h, x:x + w]

    cv2.imwrite(args["output"], stitched)
    print(f"[INFO] output image saved as {args['output']}")

else:
    print(f"[INFO] image stitching failed with status {status}")
    if status == 1:
        print("ERR_NEED_MORE_IMGS: Need more input images to construct panorama")
    elif status == 2:
        print("ERR_HOMOGRAPHY_EST_FAIL: Homography estimation failed")
    elif status == 3:
        print("ERR_CAMERA_PARAMS_ADJUST_FAIL: Camera parameter adjustment failed")