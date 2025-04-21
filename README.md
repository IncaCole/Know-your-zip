# Miami-Dade County Location Finder

This application helps you find important locations near your address or zip code in Miami-Dade County, including:

## Available Data Sources

### 🏥 Hospitals
- **Source**: Miami-Dade County Open Data
- **Endpoint**: `https://opendata.arcgis.com/datasets/MDC::hospitals.geojson`
- **Update Frequency**: Monthly
- **Fields**: Name, Address, City, Zipcode, Bed Capacity, Phone

### 🏘️ Zoning
- **Source**: Miami-Dade County Open Data
- **Endpoint**: `https://opendata.arcgis.com/api/v3/datasets/69bda17d8d1f48e58268103aebf86546_0/downloads/data?format=geojson&spatialRefId=4326`
- **Update Frequency**: Weekly
- **Fields**: Zone ID, Code, Description, Township-Range-Section

### 🏫 Schools
- **Source**: Miami-Dade County GIS
- **Endpoint**: `https://gisweb.miamidade.gov/arcgis/rest/services/MD_SchoolBoardBuffer/MapServer/1/query?where=1=1&outFields=*&f=geojson`
- **Update Frequency**: Quarterly
- **Fields**: School Name, Address, City, Zipcode, Grades, Capacity

### 🌳 Parks
- **Source**: Miami-Dade County GIS
- **Endpoint**: `https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/Parks/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&f=geojson`
- **Update Frequency**: Monthly
- **Fields**: Name, Address, City, Zipcode, Class, Total Acres, Type

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the main application:
```bash
streamlit run app.py
```

3. To validate the data sources (optional):
```bash
python test_v.py
```

## Features

- Enter your address or zip code to find nearby locations
- View distances to each location
- Sort results by distance
- Data validation tool to check API connectivity
- Support for both point and polygon geometry types
- Beautiful and modern UI with Streamlit
- Interactive maps with Folium

## Data Sources

All data is pulled from the Miami-Dade County Open Data portal and GIS services:
- https://gis-mdc.opendata.arcgis.com/
- https://gisweb.miamidade.gov/

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements or find any bugs.