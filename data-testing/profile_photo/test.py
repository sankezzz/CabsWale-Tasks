import json

def extract_user_images_simple(users_data):
   """
   Extract only aadhaar_image and profile_pic URLs from users
   Output format: {"profile_pic": "", "aadhaar_image": ""}
   """
   
   # Handle single user or list of users
   if isinstance(users_data, dict):
       users_list = [users_data]
   else:
       users_list = users_data
   
   extracted_users = []
   
   for user in users_list:
       # Check if aadhaar pic exists
       aadhaar_url = ""
       if 'aadharProfilePic' in user and user['aadharProfilePic'] and user['aadharProfilePic'].strip():
           aadhaar_url = user['aadharProfilePic']
       
       # Get profile picture URL - prioritize profile_image field, then photos array
       profile_url = ""
       
       # First check profile_image field
       if 'profile_image' in user and user['profile_image'] and user['profile_image'].strip():
           profile_url = user['profile_image']
       # If no profile_image, check photos array for the best quality image
       elif 'photos' in user and user['photos']:
           for photo in user['photos']:
               # Prefer full quality, then mob, then thumb
               if 'full' in photo and 'url' in photo['full'] and photo['full']['url']:
                   profile_url = photo['full']['url']
                   break
               elif 'mob' in photo and 'url' in photo['mob'] and photo['mob']['url']:
                   profile_url = photo['mob']['url']
                   # Continue looking for full quality
               elif 'thumb' in photo and 'url' in photo['thumb'] and photo['thumb']['url'] and not profile_url:
                   profile_url = photo['thumb']['url']
       
       # Include user only if both images are available
       if aadhaar_url and profile_url:
           user_simple = {
               "profile_pic": profile_url,
               "aadhaar_image": aadhaar_url
           }
           extracted_users.append(user_simple)
   
   return extracted_users

def process_database_file(json_file_path):
   """
   Process JSON file and extract images in simple format
   """
   try:
       with open(json_file_path, 'r', encoding='utf-8') as file:
           data = json.load(file)
       
       print(f"📁 Processing: {json_file_path}")
       print("=" * 50)
       
       # Handle different JSON structures
       if isinstance(data, list):
           users = data
           print(f"✅ Found {len(users)} users in array")
       elif isinstance(data, dict):
           if 'id' in data and 'name' in data:
               users = [data]
               print("✅ Single user detected")
           else:
               users = list(data.values())
               print(f"✅ Found {len(users)} users in object")
       else:
           print("❌ Unknown JSON structure")
           return []
       
       # Extract images
       extracted_users = extract_user_images_simple(users)
       
       print(f"🎯 Result: {len(extracted_users)} users with both images")
       print()
       
       if extracted_users:
           # Save to output file
           output_file = json_file_path.replace('.json', '_simple_output.json')
           with open(output_file, 'w', encoding='utf-8') as outfile:
               json.dump(extracted_users, outfile, indent=2, ensure_ascii=False)
           
           print(f"💾 Output saved to: {output_file}")
           print()
           print("📋 SAMPLE OUTPUT:")
           print("-" * 30)
           # Show first 3 users as sample
           for i, user in enumerate(extracted_users[:3], 1):
               print(f"{i}. {{")
               print(f'     "profile_pic": "{user["profile_pic"][:60]}...",')
               print(f'     "aadhaar_image": "{user["aadhaar_image"][:60]}..."')
               print(f"   }}")
           
           if len(extracted_users) > 3:
               print(f"   ... and {len(extracted_users) - 3} more users")
           
           return extracted_users
       else:
           print("❌ No users found with both images")
           return []
       
   except FileNotFoundError:
       print(f"❌ File not found: {json_file_path}")
       return []
   except json.JSONDecodeError as e:
       print(f"❌ JSON Error: {str(e)}")
       return []
   except Exception as e:
       print(f"❌ Error: {str(e)}")
       return []

# Test with your sample data
def test_with_sample():
   """Test with the provided sample data"""
   sample_data = [
       {
           "id": "02YCaTiF5pauIphoDL1SulxWEI03",
           "name": "Sondagar Hiren",
           "aadharProfilePic": "https://firebasestorage.googleapis.com/v0/b/bwi-cabswalle.appspot.com/o/cabswaleDrivers%2F02YCaTiF5pauIphoDL1SulxWEI03%2FaadharImage%2Faadhar_image_local.jpg",
           "profile_image": "https://firebasestorage.googleapis.com/v0/b/bwi-cabswalle.appspot.com/o/profile_images%2F2024-11-04%2015%3A21%3A46.947894.jpg",
           "photos": []
       },
       {
           "id": "04YeK5zqxaf9pBrRvWMmPWxyPCF2",
           "name": "Akil Mohammad Arshi",
           "aadharProfilePic": "https://firebasestorage.googleapis.com/v0/b/bwi-cabswalle.appspot.com/o/cabswaleDrivers%2F04YeK5zqxaf9pBrRvWMmPWxyPCF2%2FaadharImage%2F1743999450796_aadhar_image_local.jpg",
           "profile_image": "",
           "photos": [
               {
                   "full": {
                       "url": "https://firebasestorage.googleapis.com/v0/b/bwi-cabswalle.appspot.com/o/cabswaleDrivers%2F04YeK5zqxaf9pBrRvWMmPWxyPCF2%2Fphotos%2Ffull_1744166918829.jpg"
                   }
               }
           ]
       }
   ]
   
   result = extract_user_images_simple(sample_data)
   print("🧪 SAMPLE TEST RESULT:")
   print("=" * 30)
   print(json.dumps(result, indent=2))
   return result

if __name__ == "__main__":
   # Test with sample first
   test_with_sample()
   print("\n" + "="*60 + "\n")
   
   # Process your actual file
   file_path = "data.json"  # Change this to your file name
   
   print("🔍 SIMPLE IMAGE EXTRACTOR")
   print("Output format: {\"profile_pic\": \"\", \"aadhaar_image\": \"\"}")
   print()
   
   result = process_database_file(file_path)
   
   if result:
       print(f"\n✅ SUCCESS: {len(result)} users extracted")
       print("📁 Check the _simple_output.json file for complete results")
   else:
       print("\n❌ No results. Make sure your file exists and has the correct format.")

print("\n" + "="*60)
print("📖 INSTRUCTIONS:")
print("1. Save your user data as 'users_database.json'")
print("2. Run this script")
print("3. Get output in exact format: {\"profile_pic\": \"\", \"aadhaar_image\": \"\"}")
print("="*60)