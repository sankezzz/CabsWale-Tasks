from PIL import Image
from prep import MODEL,genai

gen_model=genai.GenerativeModel(MODEL)
#AP9TA9931

image=Image.open('car.jpg')
e1 = Image.open("faces/face1.JPG")
e2 = Image.open("faces/face2.JPG")
e3 = Image.open("faces/face3.JPG")
response=gen_model.generate_content(
    [
        'if the person in these images is same then return "True" else return "false"  ',
        e1,e2,e3
    ]
)
print(response.text)
output=response.text
if output=="True":
    print("faces similar ")
else :
    print("Not")






