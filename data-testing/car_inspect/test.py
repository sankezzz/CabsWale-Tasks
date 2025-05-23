import json

def extract_vehicle_data(json_file_path):
    """
    Extract vehicle images (mob type) and reg_no from JSON file
    Each verified vehicle becomes a separate JSON entry
    """
    try:
        # Load the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print(f"📁 Processing: {json_file_path}")
        print("=" * 50)
        
        # Handle different JSON structures
        if isinstance(data, list):
            users = data
        elif isinstance(data, dict):
            if 'id' in data and 'verifiedVehicles' in data:
                users = [data]  # Single user
            else:
                users = list(data.values())  # Object with users as values
        else:
            print("❌ Invalid JSON structure")
            return []
        
        print(f"✅ Processing {len(users)} users")
        
        # Extract vehicles
        vehicle_results = []
        
        for user in users:
            if 'verifiedVehicles' not in user or not user['verifiedVehicles']:
                continue
            
            # Process each verified vehicle
            for vehicle in user['verifiedVehicles']:
                reg_no = vehicle.get('reg_no', '')
                
                if not reg_no:
                    continue
                
                # Extract mob type images
                mob_images = []
                if 'images' in vehicle and vehicle['images']:
                    for image_set in vehicle['images']:
                        if 'mob' in image_set and 'url' in image_set['mob']:
                            mob_images.append(image_set['mob']['url'])
                
                # Add to results if has images
                if mob_images:
                    vehicle_entry = {
                        "number_plate": reg_no,
                        "image_urls": mob_images
                    }
                    vehicle_results.append(vehicle_entry)
        
        # Save results
        output_file = json_file_path.replace('.json', '_vehicle_output.json')
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(vehicle_results, outfile, indent=2, ensure_ascii=False)
        
        print(f"🎯 Found {len(vehicle_results)} vehicles with images")
        print(f"💾 Output saved to: {output_file}")
        
        # Show sample
        if vehicle_results:
            print("\n📋 SAMPLE OUTPUT:")
            print("-" * 30)
            for i, vehicle in enumerate(vehicle_results[:3], 1):
                print(f"{i}. Reg No: {vehicle['number_plate']}")
                print(f"   Images: {len(vehicle['image_urls'])} mob images")
                for j, img in enumerate(vehicle['image_urls'], 1):
                    print(f"     {j}. {img[:60]}...")
                print()
            
            if len(vehicle_results) > 3:
                print(f"... and {len(vehicle_results) - 3} more vehicles")
        
        return vehicle_results
        
    except FileNotFoundError:
        print(f"❌ File not found: {json_file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

if __name__ == "__main__":
    import sys
    
   
    file_path = "data.json"  # Default
    
    print("🚗 VEHICLE DATA EXTRACTOR")
    print("=" * 50)
    print(f"📁 Input file: {file_path}")
    print()
    
    # Extract vehicle data
    results = extract_vehicle_data(file_path)
    
    if results:
        print(f"\n✅ SUCCESS!")
        print(f"📊 Extracted {len(results)} vehicles")
        print("📁 Check the generated _vehicle_output.json file")
    else:
        print("\n❌ No vehicles found or processing failed")
        print("💡 Make sure your JSON file contains users with verifiedVehicles")