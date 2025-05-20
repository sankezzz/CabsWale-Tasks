import requests
from bs4 import BeautifulSoup
import json

def get_display_name(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    # If Instagram returns 404, the user doesn't exist
    if response.status_code == 404:
        return json.dumps({"error": "user dne"})

    # Sometimes Instagram returns a 200 but serves a generic "Page Not Found"
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('title').text if soup.find('title') else ""

    if "Page Not Found" in title or "Instagram" == title.strip():
        return json.dumps({"error": "user does not exist"})

    # If valid, extract display name
    if "(" in title:
        display_name = title.split('(')[0].strip()
        return json.dumps({"display_name": display_name})
    
    return json.dumps({"error": "display name not found"})

# Example usage
username = "sankezz_"  # or try a fake one like "somefakenonsenseaccountname"
print(get_display_name(username))

import requests
from bs4 import BeautifulSoup

def get_fb_display_name(username):
    url = f"https://www.facebook.com/{username}/?__a=1&__d=dis"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "user dne or request failed"}

    soup = BeautifulSoup(response.text, "html.parser")
    meta_desc = soup.find("meta", property="og:description")
    if meta_desc:
        content = meta_desc.get("content", "")
        # Usually content starts with the display name, e.g. "Virat Kohli. 4,22,11,464 ..."
        display_name = content.split(".")[0]
        return {"display_name": display_name.strip()}

    return {"error": "display name not found"}

# Usage example
print(get_fb_display_name("virat.kohli"))
