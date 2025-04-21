# Know Your Zip

A Streamlit application that helps users find nearby locations in Miami-Dade County based on their address or zip code. The application uses various Miami-Dade County Open Data APIs to provide information about nearby hospitals, schools, parks, and zoning information.

## Features

- Find nearby hospitals, schools, parks, and zoning information
- Calculate distances from user's location
- Interactive map display
- Real-time data from Miami-Dade County Open Data APIs

## Requirements

- Python 3.7+
- Streamlit
- pandas
- requests
- geopy
- folium

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/know-your-zip.git
cd know-your-zip
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
streamlit run api_list.py
```

## Data Sources

The application uses the following Miami-Dade County Open Data APIs:
- Hospitals
- Zoning
- Schools
- Parks

## License

MIT License