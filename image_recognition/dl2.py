import sys
import os
import glob
from icecream import ic

from transformers import pipeline

def make_out_filename(image_path, out_dir, ext=None):
    out_parts = image_path.split("/")
    batch = out_parts[-2]
    basename = out_parts[-1]
    out_dir = os.path.join(out_dir, batch)
    os.makedirs(out_dir, exist_ok=True)
    out_filename = os.path.join(out_dir, batch, basename)
    if ext:
        base, ext = os.path.splitext(out_filename)
        out_filename = base + ext
    return out_filename

pipe = pipeline("image-segmentation", model="briaai/RMBG-1.4", trust_remote_code=True)

for image_path in sorted(glob.glob("../records/*/P*.jpg")):
    ic(image_path)
    out_filename = make_out_filename(image_path, "dl2_out", ".png")
    
    pillow_mask = pipe(image_path, return_mask=True)
    pillow_image = pipe(image_path)

    pillow_image.save(out_filename)
    ic('wrote', out_filename)
