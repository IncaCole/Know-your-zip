from infrastructure import ParksAPI

def categorize_location(lat: float, lon: float) -> str:
    if lat >= 25.8500:  # North
        if lon >= -80.2000:  # East
            return "Northeast"
        else:
            return "Northwest"
    else:  # South
        if lon >= -80.2000:  # East
            return "Southeast"
        else:
            return "Southwest"

def main():
    # Initialize the Parks API
    parks_api = ParksAPI()
    
    # Get all parks
    parks_data = parks_api.get_all_parks()
    
    # Initialize counters for each region
    region_counts = {
        "Northeast": 0,
        "Southeast": 0,
        "Southwest": 0,
        "Northwest": 0
    }
    
    if parks_data and 'features' in parks_data:
        for park in parks_data['features']:
            if 'geometry' in park and park['geometry']:
                coords = park['geometry']['coordinates']
                # GeoJSON uses [longitude, latitude] order
                lon, lat = coords[0], coords[1]
                region = categorize_location(lat, lon)
                region_counts[region] += 1
    
    print("\nParks Distribution in Miami-Dade County:")
    print("----------------------------------------")
    for region, count in region_counts.items():
        print(f"{region}: {count} parks")
    print("----------------------------------------")

if __name__ == "__main__":
    main() 