from imutils import paths
import numpy as np
import argparse
import imutils
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", type=str, required=True,
    help="path to input directory of images to stitch")
ap.add_argument("-o", "--output", type=str, required=True,
    help="path to the output image")
args = vars(ap.parse_args())

print("[INFO] loading images...")
imagePaths = sorted(list(paths.list_images(args["images"])))
images = []

for imagePath in imagePaths:
    image = cv2.imread(imagePath)
    images.append(image)
    print(f"[INFO] loaded {imagePath}")

print("[INFO] stitching images...")
stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
(status, stitched) = stitcher.stitch(images)

if status == 0:
    print("[INFO] image stitching successful")
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