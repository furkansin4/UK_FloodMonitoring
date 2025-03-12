import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pprint import pprint
import pytz
import folium
from streamlit_folium import folium_static

st.set_page_config(
    page_title="UK Flood Monitoring",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check we are in an embedded view or not
is_embedded = st.query_params.get("embedded", "false") == "true"

# Only show the title if not embedded
if not is_embedded:
    st.title("Flood Monitoring Stations Map")

url = "https://environment.data.gov.uk/flood-monitoring/id/stations"


@st.cache_data(ttl=3600)
def get_stations():
    """
    Fetches all stations from the flood monitoring API and returns a dictionary
    with station labels as keys and station IDs as values.
    
    Returns:
        dict: Dictionary with station labels as keys and station IDs as values
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        stations = data.get('items', [])
        
        # Create dictionary with label as key and id as value
        stations_dict = {}
        station_info = []
        
        for station in stations:
            label = station.get('label', '')
            station_id = station.get('@id', '')
            lat = station.get('lat')
            long = station.get('long')
            
            # Handle case where label is a list
            if isinstance(label, list):
                # Use the first element if it's a list
                if label:
                    label = ",".join(label)
                else:
                    continue
            
            # Ensure lat and long are float values, not lists
            if isinstance(lat, list) and lat:
                lat = float(lat[0])
            elif lat is not None:
                try:
                    lat = float(lat)
                except (ValueError, TypeError):
                    continue
                    
            if isinstance(long, list) and long:
                long = float(long[0])
            elif long is not None:
                try:
                    long = float(long)
                except (ValueError, TypeError):
                    continue
            
            if label and station_id:
                stations_dict[label] = station_id
                
                # Store detailed info including coordinates for the map
                if lat is not None and long is not None:
                    station_info.append({
                        'label': label,
                        'id': station_id,
                        'lat': lat,
                        'long': long
                    })
                
        return stations_dict, station_info
    else:
        st.error(f"Failed to fetch stations: {response.status_code}")
        return {}, []

def get_readings(station_id, limit=300):
    """
    Get readings for a specific station
    """
    url = f"{station_id}/readings?_sorted&_limit={limit}"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch readings: {response.status_code}")
        return pd.DataFrame()
    
    data = response.json()
    readings = data.get('items', [])
    
    # Check if we have readings
    if not readings:
        st.warning(f"No readings found for this station")
        return pd.DataFrame()
    
    df = pd.DataFrame(readings)
    if not df.empty:
        df['dateTime'] = pd.to_datetime(df['dateTime'])
        df = df.sort_values('dateTime')
        
        # Add a column to show the reading type (extracted from the URL)
        if 'measure' in df.columns:
            df['reading_type'] = df['measure'].apply(
                lambda x: x.split('/')[-1] if isinstance(x, str) else 'unknown'
            )
        
        # Filter readings to only include the last 24 hours
        now = datetime.now(pytz.UTC)
        last_24_hours = now - timedelta(hours=24)
        df = df[df['dateTime'] >= last_24_hours]
    
    return df

def display_station_details(station_label, station_id):
    """Display the details and readings for a selected station"""
    readings = get_readings(station_id)
    
    if not readings.empty:
        st.write(f"### {station_label} Readings")
        st.write(f"Showing {len(readings)} readings")
        
        # Check if we have multiple reading types
        if 'reading_type' in readings.columns and len(readings['reading_type'].unique()) > 1:
            st.info(f"This station has multiple reading types: {', '.join(readings['reading_type'].unique())}")
            
            # Add a filter for reading types
            reading_types = list(readings['reading_type'].unique())
            selected_type = st.selectbox("Select reading type", reading_types)
            
            # Filter readings by the selected type
            filtered_readings = readings[readings['reading_type'] == selected_type]
            fig = px.line(filtered_readings, x='dateTime', y='value', title=f"Water Level Readings for {station_label}")
            st.plotly_chart(fig)
        else:
            fig = px.line(readings, x='dateTime', y='value', title=f"Water Level Readings for {station_label}")
            st.plotly_chart(fig)
    else:
        st.warning("There are no readings available for this station.")

def display_map(station_info):
    """Display a map with markers for all stations"""
    if not is_embedded:
        st.write("Click on a station marker to view its readings")
    
    # Create a map centered at the Cambridge
    m = folium.Map(location=[52.205276, 0.119167], zoom_start=10, control_scale=True)
    
    # Add markers for each station
    for station in station_info:
        # Skip if missing coordinates
        if not station.get('lat') or not station.get('long'):
            continue
            
        try:
            # Ensure coordinates are float values
            lat = float(station['lat'])
            long = float(station['long'])
            
            # Add embedded=true parameter to the URL to indicate this is an embedded view
            popup_html = f"""
            <b>{station['label']}</b><br>
            <a href="?view=detail&station={station['label']}&embedded=true">View Readings</a>
            """
            
            # Use CircleMarker instead of Marker for smaller representation
            folium.CircleMarker(
                location=[lat, long],
                radius=3,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=station['label'],
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.7
            ).add_to(m)
        except (ValueError, TypeError) as e:
            # Skip this station if coordinates can't be converted to float
            continue
    
    folium_static(m)

# Get all stations
stations_dict, station_info = get_stations()

# Navigation - determine which view to show
view = st.query_params.get("view", "map")
selected_station = st.query_params.get("station", None)

# Only show sidebar navigation if not in embedded view
if not is_embedded:
    # Sidebar for navigation
    st.sidebar.header("Navigation")
    if st.sidebar.button("Stations Map"):
        st.query_params["view"] = "map"
        st.query_params["station"] = None
        st.query_params["embedded"] = "false"
        st.rerun()

    st.sidebar.header("Station Selection")
    station_options = list(stations_dict.keys())
    
    # Set the default selected station if one was passed in query params
    default_index = 0
    if selected_station in station_options:
        default_index = station_options.index(selected_station)
    
    selected_station = st.sidebar.selectbox(
        "Select a station", 
        station_options,
        index=default_index
    )
    
    # Add button to switch stations
    if st.sidebar.button("Show Selected Station"):
        st.query_params["view"] = "detail"
        st.query_params["station"] = selected_station
        st.query_params["embedded"] = "false"
        st.rerun()


    # Add additional features section
    st.sidebar.header("Additional Features")
    if st.sidebar.button("Compare Stations"):
        st.sidebar.info("Compare functionality will be implemented soon")


# Display the appropriate view
if view == "map":
    display_map(station_info)
elif view == "detail" and selected_station:
    # Show back button only if not embedded
    if not is_embedded:
        if st.button("Back to Map"):
            st.query_params["view"] = "map"
            st.query_params["station"] = None
            st.query_params["embedded"] = "false"
            st.rerun()
    
    # Display the station details
    display_station_details(selected_station, stations_dict[selected_station])
else:
    # Default to map view if no valid view is specified
    display_map(station_info)


# Footer - only show if not in embedded view
if not is_embedded:
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center">
        <p>Data provided by the UK Environment Agency's Real-Time Flood Monitoring API</p>
        <p>This uses Environment Agency flood and river level data from the real-time data API (Beta)</p>
        <p><a href="https://environment.data.gov.uk/flood-monitoring/doc/reference" target="_blank">API Documentation</a></p>
    </div>
    """, unsafe_allow_html=True)