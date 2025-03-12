# UK Flood Monitoring Dashboard

A Streamlit application that displays real-time flood monitoring data from the UK Environment Agency's Flood Monitoring API.

## Features

- Interactive map of flood monitoring stations across the UK
- Detailed view of water level readings for each station
- Time-series visualization of water level data
- Support for multiple reading types
- Embedded view functionality for integration with other applications
- Efficient data caching system
- Location search functionality
- Handling of complex station data structures

## Technical Details

### Caching System
The application implements caching using Streamlit's `@st.cache_data` decorator with a time-to-live (TTL) of 1 hour:
- Station data is cached to reduce API calls and improve performance
- Map generation is cached to speed up navigation between views

### Location Search
- Search for stations by name using the dropdown selection in the sidebar
- Direct linking to specific stations via URL query parameters
- Persistent station selection across page refreshes

### Multiple Reading Types
- Some stations provide multiple types of readings (e.g., water level, flow rate)
- The application automatically detects and displays available reading types
- Users can switch between different reading types using a dropdown selector
- Selected reading type is preserved in URL parameters for sharing

## Data Source

This application uses Environment Agency flood and river level data from the real-time data API (Beta).
[API Documentation](https://environment.data.gov.uk/flood-monitoring/doc/reference)

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/furkansin4/UK_FloodMonitoring.git
   cd UK_FloodMonitoring
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

- The main view shows a map with all monitoring stations
- Click on a station marker to view its detailed readings
- Use the sidebar to navigate between different views
- Select different reading types when available
- Data is automatically filtered to show the last 24 hours of readings
- The application can be embedded in other websites using the `embedded=true` URL parameter

## License

This project is open source and available under the [MIT License](LICENSE). 