import torch
from sam2.sam2_image_predictor import SAM2ImagePredictor
from PIL import Image
import sys

def load_image(image_str: str) -> Image.Image:
    return Image.open(image_str).convert("RGB")

image_filename = sys.argv[1]
image = load_image(image_filename)

predictor = SAM2ImagePredictor.from_pretrained("facebook/sam2-hiera-large")

with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
    predictor.set_image(image)
    masks, _, _ = predictor.predict("album")

breakpoint()
