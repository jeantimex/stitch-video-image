from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
import os

def try_stitch_images(images, stitcher):
    """
    Attempt to stitch a list of images and return the status and result.
    """
    try:
        (status, stitched) = stitcher.stitch(images)
        return status, stitched
    except Exception as e:
        print(f"[ERROR] Exception during stitching: {e}")
        return -1, None

def adaptive_stitch(image_paths, stitcher, max_skip=3):
    """
    Adaptively stitch images, skipping problematic ones when stitching fails.
    
    Args:
        image_paths: List of image file paths in order
        stitcher: OpenCV stitcher object
        max_skip: Maximum number of consecutive images to skip
    
    Returns:
        tuple: (final_status, stitched_image, used_images, skipped_images)
    """
    if len(image_paths) < 2:
        print("[ERROR] Need at least 2 images to stitch")
        return -1, None, [], image_paths
    
    # Load first image as base
    base_image = cv2.imread(image_paths[0])
    if base_image is None:
        print(f"[ERROR] Could not load first image: {image_paths[0]}")
        return -1, None, [], image_paths
    
    used_images = [image_paths[0]]
    skipped_images = []
    current_result = base_image
    
    i = 1
    while i < len(image_paths):
        current_path = image_paths[i]
        current_image = cv2.imread(current_path)
        
        if current_image is None:
            print(f"[WARNING] Could not load image: {current_path}, skipping")
            skipped_images.append(current_path)
            i += 1
            continue
        
        print(f"[INFO] Attempting to stitch with {os.path.basename(current_path)}")
        
        # Try to stitch current result with next image
        status, stitched = try_stitch_images([current_result, current_image], stitcher)
        
        if status == 0:
            # Success - update current result and move to next image
            current_result = stitched
            used_images.append(current_path)
            print(f"[INFO] Successfully stitched {os.path.basename(current_path)}")
            i += 1
        else:
            # Failed - try to skip this image and find next compatible one
            print(f"[WARNING] Failed to stitch {os.path.basename(current_path)} (status: {status})")
            
            # Look ahead to find a compatible image
            found_compatible = False
            skip_count = 0
            
            for j in range(i + 1, min(i + max_skip + 1, len(image_paths))):
                if skip_count >= max_skip:
                    break
                
                candidate_path = image_paths[j]
                candidate_image = cv2.imread(candidate_path)
                
                if candidate_image is None:
                    continue
                
                print(f"[INFO] Trying to skip to {os.path.basename(candidate_path)}")
                
                # Try stitching with this candidate
                status, stitched = try_stitch_images([current_result, candidate_image], stitcher)
                
                if status == 0:
                    # Found compatible image
                    current_result = stitched
                    used_images.append(candidate_path)
                    
                    # Mark skipped images
                    for k in range(i, j):
                        skipped_images.append(image_paths[k])
                        print(f"[INFO] Skipped {os.path.basename(image_paths[k])}")
                    
                    print(f"[INFO] Successfully stitched {os.path.basename(candidate_path)}")
                    found_compatible = True
                    i = j + 1
                    break
                else:
                    skip_count += 1
            
            if not found_compatible:
                # No compatible image found within skip limit
                print(f"[WARNING] No compatible image found after {os.path.basename(current_path)}")
                skipped_images.append(current_path)
                i += 1
    
    return 0 if len(used_images) > 1 else -1, current_result, used_images, skipped_images

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", type=str, required=True,
    help="path to input directory of images to stitch")
ap.add_argument("-o", "--output", type=str, required=True,
    help="path to the output image")
ap.add_argument("-c", "--crop", type=int, default=0,
    help="whether to crop out largest rectangular region")
ap.add_argument("-s", "--skip", type=int, default=3,
    help="maximum number of consecutive images to skip when stitching fails")
args = vars(ap.parse_args())

print("[INFO] loading image paths...")
image_paths = sorted(list(paths.list_images(args["images"])))

if len(image_paths) < 2:
    print("[ERROR] Need at least 2 images to create a panorama")
    exit(1)

print(f"[INFO] Found {len(image_paths)} images")

print("[INFO] starting adaptive stitching...")
stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()

final_status, stitched, used_images, skipped_images = adaptive_stitch(
    image_paths, stitcher, args["skip"]
)

if final_status == 0 and stitched is not None:
    print(f"[INFO] Adaptive stitching successful!")
    print(f"[INFO] Used {len(used_images)} images: {[os.path.basename(p) for p in used_images]}")
    
    if skipped_images:
        print(f"[INFO] Skipped {len(skipped_images)} images: {[os.path.basename(p) for p in skipped_images]}")
    
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
    print("[ERROR] Adaptive stitching failed - could not create panorama")
    if used_images:
        print(f"[INFO] Successfully processed: {[os.path.basename(p) for p in used_images]}")
    if skipped_images:
        print(f"[INFO] Could not include: {[os.path.basename(p) for p in skipped_images]}")