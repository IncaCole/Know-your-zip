# Know Your ZIP

A Streamlit application that provides information about locations near a given ZIP code, including schools, hospitals, parks, and more. The app features an AI assistant powered by Llama 3 for answering questions about the local area.

## Features

- **Dashboard**: View summary statistics and detailed information about nearby locations
- **Map View**: Interactive map showing nearby points of interest
- **AI Assistant**: Chat with an AI assistant about your local area

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/know-your-zip.git
cd know-your-zip
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your Together API key:
```
TOGETHER_API_KEY=your_api_key_here
```

## Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Enter a ZIP code in the sidebar to begin exploring the data

## Data Sources

The application uses various data sources to provide information about:
- Schools
- Hospitals
- Parks
- Other points of interest

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.