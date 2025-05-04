# Cropper

Cropper is a Python script that allows you to interactively select and 
crop multiple Regions of Interest (ROIs) from each JPEG file in the input
directory. The cropped ROIs are saved as separate JPEG files in the output 
directory, together with the `rois.json` with the ROI data.

<img src="./TkGUI.png" alt="Cropper" width="600"/>

## Usage

To use the Cropper script, follow these steps:

```bash
git clone github.com/olafrv/cropper.git
cd cropper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 cropper.py --input_dir composite/ --output_dir extracts/
```
