import requests
import pandas as pd
from api_list import API_ENDPOINTS
from tabulate import tabulate
from datetime import datetime

def validate_data():
    print("\n=== MIAMI-DADE COUNTY API TEST ===")
    print("Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)
    
    results_summary = []
    
    for category, endpoint in API_ENDPOINTS.items():
        print(f"\n📍 Testing {category.upper()} API...")
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()
            
            if 'features' in data:
                features = []
                for feature in data['features']:
                    properties = feature.get('properties', {})
                    geometry = feature.get('geometry', {})
                    if geometry:
                        # Handle different geometry types
                        if geometry.get('type') == 'Point':
                            coordinates = geometry.get('coordinates', [])
                            if len(coordinates) >= 2:
                                properties['latitude'] = coordinates[1]
                                properties['longitude'] = coordinates[0]
                        elif geometry.get('type') == 'Polygon':
                            # For polygons, use the first coordinate of the first ring
                            coordinates = geometry.get('coordinates', [[]])
                            if coordinates and coordinates[0] and len(coordinates[0][0]) >= 2:
                                properties['latitude'] = coordinates[0][0][1]
                                properties['longitude'] = coordinates[0][0][0]
                    features.append(properties)
                    
                df = pd.DataFrame(features)
                
                # Add to summary
                results_summary.append({
                    'API': category,
                    'Status': '✅ CONNECTED',
                    'Records': len(df),
                    'Fields': len(df.columns)
                })
                
                # Print data preview
                print("\n📊 Data Sample:")
                print("-" * 50)
                print(f"Total records: {len(df)}")
                print(f"Available fields: {len(df.columns)}")
                print("\n🔍 First 5 records:")
                
                # Select important columns for display
                display_cols = ['name', 'address', 'latitude', 'longitude'] if 'name' in df.columns else df.columns[:4]
                preview_df = df[display_cols].head()
                print(tabulate(preview_df, headers='keys', tablefmt='pretty', showindex=False))
                
                print("\n📋 All Available Fields:")
                print(", ".join(df.columns.tolist()))
                
            else:
                results_summary.append({
                    'API': category,
                    'Status': '❌ NO DATA',
                    'Records': 0,
                    'Fields': 0
                })
                print("❌ No features found in data")
                
        except requests.exceptions.RequestException as e:
            results_summary.append({
                'API': category,
                'Status': '❌ ERROR',
                'Records': 0,
                'Fields': 0
            })
            print(f"❌ Error: {str(e)}")
        
        print("-" * 50)
    
    # Print final summary table
    print("\n📑 API CONNECTION SUMMARY")
    print("=" * 50)
    summary_df = pd.DataFrame(results_summary)
    print(tabulate(summary_df, headers='keys', tablefmt='grid', showindex=False))

if __name__ == "__main__":
    validate_data() 