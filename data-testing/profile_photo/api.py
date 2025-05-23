import json
import requests
import time

def send_to_api(user_data, api_url):
    """
    Send user data to API endpoint - BLOCKS until response received
    """
    try:
        print("⏳ Sending request...")
        
        # This line BLOCKS until response is received
        response = requests.post(
            api_url, 
            json=user_data,
            headers={'Content-Type': 'application/json'},
            timeout=30  # Wait up to 30 seconds for response
        )
        
        print(f"📨 Response received (Status: {response.status_code})")
        
        return {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response': response.json() if response.status_code == 200 else response.text,
            'error': None
        }
        
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 30 seconds")
        return {
            'status_code': None,
            'success': False,
            'response': None,
            'error': 'Request timeout (30s)'
        }
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return {
            'status_code': None,
            'success': False,
            'response': None,
            'error': f'Request error: {str(e)}'
        }

def process_users_sequentially(json_file_path, api_url, limit=5):
    """
    Process users ONE BY ONE - each request waits for previous to complete
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            users_data = json.load(file)
        
        print(f"📁 Loaded {len(users_data)} users")
        print(f"🔄 Processing {limit} users SEQUENTIALLY")
        print("=" * 60)
        
        results = []
        
        for i, user in enumerate(users_data[:limit], 1):
            print(f"\n🎯 USER {i}/{limit} - STARTING")
            print("-" * 40)
            print(f"Profile: {user['profile_pic'][:50]}...")
            print(f"Aadhaar: {user['aadhaar_image'][:50]}...")
            
            # CRITICAL: This call BLOCKS until API responds
            start_time = time.time()
            api_result = send_to_api(user, api_url)
            end_time = time.time()
            
            # Process result
            result = {
                'user_index': i,
                'processing_time_seconds': round(end_time - start_time, 2),
                'input_data': user,
                'api_result': api_result
            }
            results.append(result)
            
            # Show result
            if api_result['success']:
                print(json.dumps(api_result['response'], indent=2))
            else:
                print(f"❌ USER {i} FAILED after {result['processing_time_seconds']}s")
                print(f"Error: {api_result['error']}")
            
            print(f"🏁 USER {i} FINISHED")
            
            # Only proceed to next user after current one is complete
            if i < 10:
                print(f"\n⏳ Waiting 3 seconds before USER {i+1}...")
                time.sleep(3)  # Optional delay between users
        
        # Save results
        output_file = json_file_path.replace('.json', '_sequential_results.json')
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(results, outfile, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Summary
        successful = sum(1 for r in results if r['api_result']['success'])
        total_time = sum(r['processing_time_seconds'] for r in results)
        
        print(f"\n📊 FINAL SUMMARY:")
        print(f"   • Total users processed: {len(results)}")
        print(f"   • Successful: {successful}")
        print(f"   • Failed: {len(results) - successful}")
        print(f"   • Total processing time: {total_time:.2f} seconds")
        print(f"   • Average time per user: {total_time/len(results):.2f} seconds")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

if __name__ == "__main__":
    # Configuration
    json_file = "data_simple_output.json"  # Your file
    api_endpoint = "https://us-central1-cabswale-test.cloudfunctions.net/inspect_profile_pic_resized"
    
    print("🔄 SEQUENTIAL API PROCESSOR")
    print("=" * 60)
    print("⚡ Each request waits for previous to complete")
    print(f"📁 Input: {json_file}")
    print(f"🌐 API: {api_endpoint}")
    print(f"🎯 Limit: 5 users")
    
    # Process sequentially
    results = process_users_sequentially(json_file, api_endpoint, limit=5)
    
    if results:
        print("\n🎉 All users processed successfully!")
    else:
        print("\n❌ Processing failed. Check your file and API.")