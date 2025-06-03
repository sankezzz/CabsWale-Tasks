from PIL import Image
from prep import MODEL,genai
import json
import re
import os
gen_model=genai.GenerativeModel(MODEL)
#AP9TA9931

image=Image.open('car.jpg')
e1 = Image.open("faces/face4.JPG")
e2 = Image.open("faces/face2.JPG")
e3 = Image.open("faces/rock.jpeg")
person_id=Image.open("faces/adhar.jpg")
response=gen_model.generate_content(
    [
       """
You will be given 3 or more images.

Your task is to:
1. Detect if **each image** contains a **valid human face**.
2. If **any image** does NOT contain a face, return a JSON that only reports which images are missing faces and **skip the similarity analysis**.
3. If **all images** contain a valid face, then:
   - Compare the faces to check if they belong to the **same person**.
   - Calculate a confidence score.
   - Identify which image(s) are mismatched, if any.
4. there is also an id of the person in this so i will need you to detect the face from the id and 

### Step 1: Face Detection

If any face is missing, return:
{
  "same_person": false,
  "confidence": 0.0,
  "mismatched_images": ["imageX"],
  "face_detection": {
    "image1": true,
    "image2": false,
    ...
  },
}

### Step 2: Face Comparison

If all faces are detected, return:
{
  "same_person": true or false,
  "confidence": float (0 to 1),
  "mismatched_images": ["imageX", "imageY"],
  "face_detection": {
    "image1": true,
    "image2": true,
    ...
  },
}

### Additional Instructions:
- Use image labels: image1, image2, image3, ..., imageN
- Always return only a valid JSON object — no extra text, formatting, or markdown 
  "same_person": false,
  "confidence": 0.65,
  "mismatched_images": ["image3"],
  "face_detection": {
    "image1": true,
    "image2": true,
    "image3": true
  }
} like this.
- `mismatched_images` should include:
  - Any image with missing faces
  - Any image with a different face
- `confidence` should reflect overall similarity confidence
-the output must be only a json component starting from { and ending with }

"""

,
        e1,e2,e3
    ]
)
print(response)
output=response.text


#parses the output to get us the json only
match = re.search(r'\{.*\}', output, re.DOTALL)
if match:
    json_str = match.group(0)
    json_data = json.loads(json_str)
    # print(json.dumps(json_data, indent=2))
else:
    print("No JSON found.")
#json for this instance is stored in json_data
#this will give us the data stored in json 
file_path = "output.json"

# Check if file exists
if os.path.exists(file_path):
    with open(file_path, "r+") as f:
        try:
            existing_data = json.load(f)
            if not isinstance(existing_data, list):
                existing_data = [existing_data]
        except json.JSONDecodeError:
            existing_data = []

        existing_data.append(json_data)
        f.seek(0)
        json.dump(existing_data, f, indent=2)
        f.truncate()
else:
    # Create a new file with a list
    with open(file_path, "w") as f:
        json.dump([json_data], f, indent=2)



