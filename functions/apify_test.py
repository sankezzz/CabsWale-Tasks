import requests

API_TOKEN = ''
url = f"https://api.apify.com/v2/acts/drobnikj~instagram-scraper/run-sync-get-dataset-items?token={API_TOKEN}"

payload = {
    "usernames": ["natgeo"],
    "resultsLimit": 2,
    "scrapePosts": True,
    "scrapeProfile": True
}

response = requests.post(url, json=payload)
data = response.json()
print(data)
