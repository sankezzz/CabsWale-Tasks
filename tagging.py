from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def get_instagram_profile_data(username):
    # Setup headless Chrome
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    url = f"https://www.instagram.com/{username}/"
    driver.get(url)

    time.sleep(5)  # Let page load completely

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup)
    # Get bio
    bio_section = soup.find('meta', property="og:description")
    bio = bio_section["content"] if bio_section else "No bio found"
    print(bio_section)
    # Get images
    images = []
    for img in soup.find_all('img'):
        images.append(img['src'])

    driver.quit()
    return {
        "bio": bio,
        "images": images[:5], 
        "content":bio_section
    }
    

# Example usage
data = get_instagram_profile_data('cab_driver__')
print("Bio:", data['bio'])
print(data['content'])

print("Images:", data['images'])

# now we will be giving this data to gemini to tell us about the person 
from prep import genai, MODEL

gen_model = genai.GenerativeModel(MODEL)

response = gen_model.generate_content([
    f'''You are a profiling AI. Based on the following Instagram data, assign relevant tags to the drivers of cabs and give specific tags:
    Personality Tags:
calm_driver, aggressive_driver, respectful, talkative, rude_driver, humorous, silent_type

Lifestyle Tags:
family_man, bachelor_lifestyle, religious, party_goer, early_riser, smoker_driver, pet_lover

Driving Style Tags:
clean_cab, loud_music_lover, decorated_cab, reckless_driver, disciplined

Passenger Attitude Tags:
polite_service, foodie_driver, helper_nature, women_friendly, rude_to_passengers

Risk Flags Tags:
suspicious_profile, offensive_content, alcohol_usage, fake_location_tags, aggressive_reels

Interest Tags:
bike_enthusiast, travel_freak, foodie, vlogger_driver, reel_creator

in tags section just sum up all the tags that are detected

Bio:
"{data['bio']}"

Images (descriptions of what you see in them):
{data['images']}

Return tags in JSON format like:
{{
  "personality": "...",
  "lifestyle": "...",
  "risk_level": "...",
  "tags": ["..."]
  "age":".."
}}
just give me this json format in output no other things and no othere text only json '''
])

print(response.text)
