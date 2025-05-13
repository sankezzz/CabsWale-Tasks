from PIL import Image
from prep import MODEL,genai

gen_model=genai.GenerativeModel(MODEL)
#AP9TA9931
image=Image.open('car.jpg')
user_car_number=input("Give your car number")
response=gen_model.generate_content(
    [
        'Extract the number plate given in image and give it without spacing',
        image
    ]
)
print(response.text)
detected_number=response.text

if detected_number==user_car_number:
    print("THe number matches")
else:
    print("The number dosent match")






