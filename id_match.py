#we have an input of two images of the addhar and driving licence and we need to get the output that the name on both of them must be same 
#we must consider all the edge cases that might occour in this with middle name and other things 
#spelling diffreaces and other things should be included in this 
from PIL import Image
from prep import MODEL,genai
import re 
import os 
import json



gen_model=genai.GenerativeModel(MODEL)
image1=Image.open('faces/pan.jpg')
image2=Image.open('faces/adhar.jpg')
response=gen_model.generate_content(
    [
       '''you are given two images of a persons ids we need to detect the name from both of these and check wether the names on both of thers

Return the result as a JSON array of car objects.
Example format:
[
  {
    "number_plate": "AP9TA9931",
    "make_model": "Hyundai i10",
    "color": "White",
    "estimated_year": "2017",
    "condition": "Good"
  }
]
''',
        image
    ]
)
print(response.text)
detected_data=response.text 

match = re.search(r'\{.*\}', detected_data, re.DOTALL)
if match:
    json_str = match.group(0)
    json_data = json.loads(json_str)
    # print(json.dumps(json_data, indent=2))
else:
    print("No JSON found.")
#json for this instance is stored in json_data
#this will give us the data stored in json 
file_path = "car_output.json"

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














