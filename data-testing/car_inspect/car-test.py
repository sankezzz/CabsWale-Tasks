import json
import requests
import time

def send_vehicle_request(vehicle_data, api_url):
    """Send POST request and return only the API JSON response"""
    try:
        response = requests.post(
            api_url,
            json=vehicle_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "message": response.text}
            
    except requests.exceptions.Timeout:
        return {"error": "timeout", "message": "Request timed out after 60 seconds"}
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

def process_vehicle_file(json_file_path, api_url, limit=10):
    """Process vehicle file and send requests sequentially for first N vehicles"""
    
    # Load vehicle data
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            vehicles_data = json.load(f)
        
        # Limit to first N vehicles
        vehicles_data = vehicles_data[:limit]
        
        print(f"Loaded {len(vehicles_data)} vehicles from {json_file_path} (limited to first {limit})")
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    # Prepare output file
    timestamp = int(time.time())
    output_file = f"api_responses_first_{limit}_{timestamp}.json"
    api_responses = []
    
    print(f"API Endpoint: {api_url}")
    print(f"Output file: {output_file}")
    print("="*60)
    
    # Process each vehicle sequentially
    for i, vehicle in enumerate(vehicles_data, 1):
        print(f"\nRequest {i}/{len(vehicles_data)} - Plate: {vehicle.get('number_plate', 'Unknown')}")
        print("-" * 40)
        
        # Send request (BLOCKS until complete)
        start_time = time.time()
        api_response = send_vehicle_request(vehicle, api_url)
        end_time = time.time()
        
        # Show API response on console
        print("API Response:")
        print(json.dumps(api_response, indent=2))
        print(f"Processing time: {end_time - start_time:.2f}s")
        
        # Save to list
        api_responses.append(api_response)
        
        # Wait before next request (except for last one)
        if i < len(vehicles_data):
            print("\nWaiting 2 seconds...")
            time.sleep(2)
    
    # Save all API responses to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(api_responses, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"Total requests: {len(vehicles_data)} (first {limit} vehicles)")
    print(f"Responses saved to: {output_file}")

if __name__ == "__main__":
    # Configuration
    
    vehicle_file = "data_vehicle_output.json"  # Default
    
  
    api_endpoint = "https://inspect-car-optimised-7cijur72sa-uc.a.run.app"  # Default
    
    # Process only first 10 vehicles
    process_vehicle_file(vehicle_file, api_endpoint, limit=10)