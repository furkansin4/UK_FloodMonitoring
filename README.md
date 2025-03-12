# UK Flood Monitoring Dashboard

A Streamlit application that displays real-time flood monitoring data from the UK Environment Agency's Flood Monitoring API.

## Features

- Interactive map of flood monitoring stations across the UK
- Detailed view of water level readings for each station
- Time-series visualization of water level data
- Support for multiple reading types
- Embedded view functionality for integration with other applications

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

## License

This project is open source and available under the [MIT License](LICENSE). 