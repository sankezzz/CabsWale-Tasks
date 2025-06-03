
import requests
import time
import json
import os 
APIFY_TOKEN=''
USERNAME = 'sankezzz'  # Replace with the Instagram username

def run_instagram_scraper(username):
    username = username.strip().lower()

    # Step 1: Start the run
    url = f'https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs?token={APIFY_TOKEN}'

    payload = {
        "usernames": [username],
        "resultsLimit": 1,
        "resultsType": "details",
        "mediaLimit": 1
    }

    print(f"[+] Starting Instagram scrape for @{username}...")
    run_res = requests.post(url, json=payload)
    run_data = run_res.json()

    if 'data' not in run_data:
        raise Exception("❌ Failed to start actor. Check token or username.")

    run_id = run_data['data']['id']

    # Step 2: Poll for completion
    while True:
        status_url = f'https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}'
        status_res = requests.get(status_url).json()
        status = status_res['data']['status']
        print(f"[*] Scraper status: {status}")
        if status in ['SUCCEEDED', 'FAILED', 'ABORTED']:
            break
        time.sleep(3)

    if status != 'SUCCEEDED':
        raise Exception(f"❌ Scraper run failed: {status}")

    # Step 3: Fetch scraped dataset
    dataset_id = status_res['data']['defaultDatasetId']
    dataset_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true&format=json'
    raw_data = requests.get(dataset_url).json()

    if not raw_data or not isinstance(raw_data, list):
        raise Exception("❌ No valid data returned from Apify.")

    user_info = raw_data[0]
    posts = raw_data[0].get("latestPosts", [])[:5]

    minimal_data = {
        "username": user_info.get("username", "N/A"),
        "fullName": user_info.get("fullName", "N/A"),
        "biography": user_info.get("biography", "N/A"),
        "followersCount": user_info.get("followersCount", "N/A"),
        "recentPosts": [
            {
                "caption": post.get("caption", ""),
                "imageUrl": post.get("displayUrl", "")
            }
            for post in posts if post.get("displayUrl")
        ]
    }

    return minimal_data

if __name__ == '__main__':
    try:
        result = run_instagram_scraper(USERNAME)
        print("\n✅ Final Result:\n")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print("\n❌ Error:", e)
