import json 
import time 
import requests 

usernames=["cristiano", "leomessi", "selenagomez", "kyliejenner", "zendaya",
    "kimkardashian", "anushkasharma", "deepikapadukone", "shraddhakapoor", "sidharthmalhotra",
    "diljitdosanjh", "kritisanon", "aliaabhatt", "ranveersingh", "vickykaushal09",
    "norafatehi", "tigerjackieshroff", "dishapatani", "kartikaaryan", "kiaraaliaadvani"]

result_response=[]

endpoint='http://127.0.0.1:5001/cabswale-test/us-central1/scrape_instagram'

for username in usernames:
    payload={
        "username":username
    }

    try:
        response=requests.post(endpoint,json=payload)
        if response.status_code==200:
            data=response.json()
            print(f"recieved data for {username}")
        else:
            data = {"username": username, "error": f"Status code: {response.status_code}"}
            print(f"⚠️ Failed for {username}: {response.status_code}")

    except Exception as e:
        data = {"username": username, "error": str(e)}
        print(f"❌ Exception for {username}: {str(e)}")

    result_response.append(data)

    time.sleep(1)

    with open("Instagram user data saved","w") as f:
        json.dump(result_response,f,indent=2)
    print("all data saved")