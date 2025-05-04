#!/usr/bin/env python3

"""
Author: Olaf Reitmaier Veracierta <olafrv@gmail.com> 04.May.2025

Description:

This script extracts photos from a folder of composite images.
It uses OpenCV to detect contours and crops the images accordingly.

The script assumes that the images are in JPEG format and are located
in a folder named 'composites'. The extracted images are saved in a 
folder named 'extracts' with the same name as the original image, 
followed by an underscore and a number.

The script uses the following steps:
1. Read the image using OpenCV.
2. Convert the image to grayscale.
3. Apply Gaussian blur to the grayscale image.
4. Detect edges using Canny edge detection.
5. Find contours in the edged image.
6. Sort the contours from left to right and top to bottom.
7. Loop through the contours and filter out small ones.
8. For each valid contour, crop the image and save it with a new name.
"""

import cv2
import os
from pathlib import Path

def extract_photos_from_folder(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for file in input_path.glob("*.jpg"):

        # Read the image
        print(f"Processing {file.name}")
        image = cv2.imread(str(file))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Blur and detect edges
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)

        # Find contours
        contours, _ = cv2.findContours(
            edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours left to right, top to bottom (optional)
        contours = sorted(
            contours, 
            key=lambda c: cv2.boundingRect(c)[1] 
                * image.shape[1] + cv2.boundingRect(c)[0]
        )

        photo_count = 0
        base_name = file.stem

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # Filter small contours
            if w > 100 and h > 100:
                cropped = image[y:y+h, x:x+w]
                photo_count += 1
                out_file = output_path / f"{base_name}_{photo_count}.jpg"
                cv2.imwrite(str(out_file), cropped)

        print(f"Extracted {photo_count} photos from {file.name}")

# Run it
extract_photos_from_folder("composites", "extracts")
