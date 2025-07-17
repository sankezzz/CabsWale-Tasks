from PIL import Image
from prep import MODEL, genai
import json
import re
import os

# Initialize model
gen_model = genai.GenerativeModel(MODEL)

# Load images dynamically (add your image paths here)
image_paths = [
    "faces/face2.jpg",
    "faces/face3.jpg",
    "faces/face5.jpg",
    "faces/adhar.jpg"
    
]

# Minimum 3 images required
if len(image_paths) < 3:
    raise ValueError("At least 3 images are required to proceed.")

# Open images
image_objects = [Image.open(img_path) for img_path in image_paths]

# Generate prompt
instruction_prompt = """
You will be given 3 or more images.

Your task is to:
1. Detect if **each image** contains a **valid human face**.
2. If **any image** does NOT contain a face, return a JSON that only reports which images are missing faces.
3. If **all images** contain a valid face, then:
   - Compare the faces to check if they belong to the **same person**.
   - Calculate a confidence score.
   - Identify which image(s) are mismatched, if any.
4. there is also an id of the person in this so i will need you to detect the face from the id and check wehter the face from the uploaded images is the same as the face from the id 
this must be precise and 100 percent accurate consider some images might be blur and low light so use some image processing i them to 

### Step 1: Face Detection

If any face is missing, return:
{
  "same_person": false,
  "id_match":"",
  "match_confidence": 0.0,
  "mismatched_images": [],
  "face_not_detected": ["imageX", "imageY"]
}

### Step 2: Face Comparison

If all faces are detected, return:
{
  "same_person": true or false,
  "id_match":"",
  "match_confidence": float (0 to 1),
  "mismatched_images": ["imageX", "imageY"],
  "face_not_detected": []
}

### Additional Instructions:
- Use image labels: image1, image2, image3, ..., imageN
- Always return only a valid JSON object — no extra text, formatting, or markdown.
- The output must be only a JSON component starting from { and ending with }.
"""

# Prepare input
input_list = [instruction_prompt] + image_objects

# Call the model
response = gen_model.generate_content(input_list)
output = response.text.strip()

# Parse JSON response
match = re.search(r'\{.*\}', output, re.DOTALL)
if not match:
    raise ValueError("No JSON object found in response.")

json_str = match.group(0)
json_data = json.loads(json_str)

print(json_str)

