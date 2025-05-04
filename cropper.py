#!/usr/bin/env python3

"""
Author: Olaf Reitmaier Veracierta <olafrv@gmail.com> 04.May.2025

Description:

Cropper is a Python script that allows you to interactively select and 
crop multiple Regions of Interest (ROIs) from each JPEG file in the input
directory. The cropped ROIs are saved as separate JPEG files in the output 
directory, together with the `rois.json` with the ROI data.

This script processes JPEG images in four main steps:
1. Load (if existing) Regions of Interest (ROIs) from a JSON file.
2. Allow user to interactively select (new) Regions of Interest (ROIs).
3. Save the ROIs for each image in a JSON file in the output directory.
4. Save cropped ROIs extracted images in the output directory.

Usage:
    python cropper.py --input_dir <path_to_input_directory> \
        [--output_dir <path_to_output_directory>]

Arguments (Required):
    --input_dir, -i   Path to the directory containing JPEG files.
    --output_dir, -o  Directory to save cropped images and ROI data.

Dependencies:
    - OpenCV (cv2)
    - Tkinter
    - JSON
"""

import os
import cv2
import argparse
import tkinter as tk
import json

def load_rois(rois_dir: str, id: str) -> list:
    filepath = os.path.join(rois_dir, 'rois.json')
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            rois_data = json.load(file)
            if id in rois_data:
                return rois_data[id]    
    return []
          
def save_rois(rois_dir: str, id: str, rois: list):
    rois_dict = {}
    filepath = os.path.join(rois_dir, 'rois.json')
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            rois_dict = json.load(file)
    
    rois_dict[id] = rois
    with open(filepath, 'w') as file:
        json.dump(rois_dict, file, indent=2)

def process_images(input_dir, output_dir=None):
    if input_dir is None or not os.path.isdir(input_dir):
        raise ValueError("An input directory must be provided.")
    if output_dir is None or not os.path.isdir(output_dir):
        raise ValueError("An output directory must be provided.")

    # Determine screen height for resizing and centering
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    for filename in sorted(os.listdir(input_dir)):
        
        # Skip non-JPEG files
        if not filename.lower().endswith(('.jpg', '.jpeg')):
            print(f"Skipping non-JPEG file: {filename}")
            continue
        
        # Load image
        print(f"\nProcessing: {filename}")
        filepath = os.path.join(input_dir, filename)
        image = cv2.imread(filepath)
        if image is None:
            print(f"Warning: failed to load {filepath}")
            continue

        # Determine scale: Must be 70% of the screen height
        # to fit the image in the center of the screen
        # and leave space for the menu/task bar.
        h, w = image.shape[:2]
        if h > screen_height:
            scale = screen_height / float(h) * 0.7  # Menu/Task Bar
        else:
            scale = 0.7

        print(f"  Screen size: {screen_width}w x {screen_height}h")
        print(f"  Image size: {w}w x {h}h, Target Scale: {scale:.2f}")
        print(f"  Image size (scaled): {int(w * scale)}w x {int(h * scale)}h")


        # Resize for display
        disp_w, disp_h = int(w * scale), int(h * scale)
        disp_image = cv2.resize(image, (disp_w, disp_h))

        # If existing ROIs saved, draw them on display
        rois = load_rois(rois_dir=output_dir, id=filename)
        for box in rois:
            x0, y0, x1, y1 = box
            # scale coordinates
            sx0, sy0 = int(x0 * scale), int(y0 * scale)
            sx1, sy1 = int(x1 * scale), int(y1 * scale)
            cv2.rectangle(disp_image, (sx0, sy0), (sx1, sy1), (0, 255, 0), 2)

        # Let user select multiple ROIs in an interactive window; use the mouse
        # to draw rectangles. Press ENTER or SPACE when done to confirm the 
        # selections, or ESC to skip the selection process.
        sel_win = f"Select ROIs - {filename}"
        pos_x = max((screen_width - disp_w) // 2, 0)
        # The first division by 2 is to center the window in the screen
        # and the second division by 2 is to leave space for the menu/task bar.
        pos_y = max((screen_height - disp_h) // 2 // 2, 0)
        cv2.namedWindow(sel_win, cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow(sel_win, pos_x, pos_y)
        rois_new = cv2.selectROIs(
            windowName=sel_win,
            img=disp_image,
            showCrosshair=True,
            fromCenter=False
        )
        cv2.destroyAllWindows()
        if len(rois_new) == 0:
            print("  No new ROIs selected.")
            continue

        # Convert displayed ROIs back to original coordinates
        for (x, y, w_box, h_box) in rois_new:
            x0 = int(x / scale)
            y0 = int(y / scale)
            x1 = int((x + w_box) / scale)
            y1 = int((y + h_box) / scale)
            rois.append([x0, y0, x1, y1])

        # Persist ROIs
        print(f"  Saving ROIs for {filename}... {len(rois)} ROIs")
        save_rois(rois_dir=output_dir, id=filename, rois=rois)

        # Save crops
        base, ext = os.path.splitext(filename)
        for idx, (x0, y0, x1, y1) in enumerate(rois, start=1):
            crop = image[y0:y1, x0:x1]
            out_name = f"{base}_{idx}{ext}"
            out_path = os.path.join(output_dir, out_name)
            cv2.imwrite(out_path, crop)
            print(f"  Saved crop {idx}: {out_name}")


def main():
    parser = argparse.ArgumentParser(
        description='Iterate over JPEG images, ask for ROIs and save crops.'
    )
    parser.add_argument(
        '--input_dir', '-i',
        help='Path to the directory containing JPEG files.',
        required=True
    )
    parser.add_argument(
        '--output_dir', '-o',
        help='Directory to save cropped images and ROI data.',
        required=True
    )
    args = parser.parse_args()
    process_images(args.input_dir, args.output_dir)


if __name__ == '__main__':
    main()