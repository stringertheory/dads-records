import sys
import os
import json

import google.generativeai as genai
from PIL import Image, ImageDraw

def main():

    image_filename = sys.argv[1]
    
    genai.configure(api_key=os.getenv("GOOGLE_GEMINI"))
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
    goats = Image.open(image_filename)
    prompt = 'The image is a photo of an album cover sitting on a dark table. Return the bounding box of the part of the album cover that shows the catalog number. Return [ymin, xmin, ymax, xmax]'
    response = model.generate_content([goats, prompt])
    ymin, xmin, ymax, xmax = json.loads(response.text)
    ymin = (ymin / 1000) * goats.height
    ymax = (ymax / 1000) * goats.height
    xmin = (xmin / 1000) * goats.width
    xmax = (xmax / 1000) * goats.width
    
    goats1 = ImageDraw.Draw(goats)
    goats1.rectangle([xmin, ymin, xmax, ymax], fill=None, outline="red")

    goats.show()


if __name__ == "__main__":
    main()
