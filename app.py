import streamlit as st
import numpy as np
import pandas as pd
import folium
from datetime import datetime, timedelta
import requests


# Constants
BING_MAPS_API_KEY = "AvyY7OGE3G5E6Y7rdLxsEXTsAb89nxSGNmtVLWf5OXgxF61xZPlWGRF6fXtirFf0"
TRUCK_CAPACITY = 1000  # Assuming truck capacity in terms of product units
SALARY_PER_HOUR = 500  # Salary of driver per hour in rupees
TRUCK_MILEAGE = 5  # Truck mileage in kilometers per liter
DIESEL_COST_PER_LITER = 100  # Cost of diesel per liter in rupees
NUM_TRUCKS = 1  # Number of trucks

# Locations (latitude, longitude, diesel price per liter) - Example
df = pd.read_csv('cities.csv')
locations1 = {}

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    city_name = row['City']
    latitude = row['Lat']
    longitude = row['Long']
    locations1[city_name] = (latitude, longitude)

st.title("ALL_IN_RED")
st.subheader("Navigation for the real world")

def searchable_multiselect(label, options):
    selected_options = st.multiselect(label, options)
    if "Type here..." in selected_options:
        custom_option = st.text_input("Enter custom value:")
        if custom_option:
            selected_options.append(custom_option)
    return selected_options

# Calculate distance matrix using Bing Maps API
def calculate_distance_matrix(locations, api_key):
    n = len(locations)
    distance_matrix = np.zeros((n, n))
    for i, (origin_name, origin_coord) in enumerate(locations.items()):
        for j, (dest_name, dest_coord) in enumerate(locations.items()):
            if i != j:
                url = f"http://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?key={api_key}&origins={origin_coord[0]},{origin_coord[1]}&destinations={dest_coord[0]},{dest_coord[1]}&travelMode=driving"
                response = requests.get(url)
                data = response.json()
                if 'resourceSets' in data and data['resourceSets'] and 'resources' in data['resourceSets'][0] and data['resourceSets'][0]['resources'] and 'results' in data['resourceSets'][0]['resources'][0]:
                    distance_matrix[i][j] = data['resourceSets'][0]['resources'][0]['results'][0]['travelDistance']
                else:
                    print("Error retrieving distance data for", origin_name, "->", dest_name)
                    distance_matrix[i][j] = float('inf')  # Assigning a large value for error handling
    return distance_matrix

# Nearest neighbor algorithm
def nearest_neighbor(distances, start=0):
    n = len(distances)
    unvisited = set(range(n))
    unvisited.remove(start)
    path = [start]
    current = start
    while unvisited:
        nearest = min(unvisited, key=lambda x: distances[current, x])
        path.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    return path

# Optimize route using 2-opt
def optimize_route(route, distances):
    n = len(route)
    best_route = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n):
                if j - i == 1:
                    continue
                new_route = route[:]
                new_route[i:j + 1] = route[j:i - 1:-1]
                if total_distance(new_route, distances) < total_distance(best_route, distances):
                    best_route = new_route
                    improved = True
        route = best_route
    return route

def calculate_arrival_times(destinations_times):
    # Automatically initialize departure time as current time
    departure_time = datetime.now()

    arrival_times = []
    current_time = departure_time
    for t in destinations_times:
        # Parse time string to get timedelta
        delta = timedelta()
        if 'day' in t:
            days, time = t.split(", ")
            day_delta = timedelta(days=int(days.split()[0]))
            delta += day_delta
            t = time

        h, m, s = map(int, t.split(':'))
        time_delta = timedelta(hours=h, minutes=m, seconds=s)
        delta += time_delta

        # Add the break time if not for the first destination
        if arrival_times:
            delta += timedelta(hours=3)

        # Update the current time and append to arrival_times
        current_time += delta
        arrival_times.append(current_time)

    return arrival_times

# Calculate total distance of a route
def total_distance(route, distances):
    total = 0
    for i in range(len(route) - 1):
        total += distances[route[i], route[i+1]]
    return total


# Solve the optimization problem
def optimize_routes(locations, truck_capacity, distance_matrix):
    routes = []
    for i in range(NUM_TRUCKS):
        if i == 0:
            start_location = list(locations.keys())[0]
        else:
            start_location = routes[i - 1][-1]
        remaining_locations = list(locations.keys())
        remaining_locations.remove(start_location)
        path = nearest_neighbor(distance_matrix, list(locations.keys()).index(start_location))
        path = optimize_route(path, distance_matrix)
        routes.append([start_location] + [list(locations.keys())[i] for i in path])
    return routes

# Calculate total hours required for the journey
def total_hours(distance_matrix):
    total_distance = np.sum(distance_matrix)
    total_hours = total_distance / TRUCK_MILEAGE  # Assuming constant speed
    return total_hours

# Function to calculate total distance, toll charges, and time


# Constants
BING_MAPS_API_KEY = "AvyY7OGE3G5E6Y7rdLxsEXTsAb89nxSGNmtVLWf5OXgxF61xZPlWGRF6fXtirFf0"

# Function to calculate total distance, toll charges, and time
def calculate_route_metrics(route):
    total_distance = 0
    total_toll_charges = 0
    total_time = 0
    time1 = []

    for i in range(len(route) - 1):
        origin = route[i]
        destination = route[i + 1]
        
        # Construct Bing Maps API URL for route details
        url = f"http://dev.virtualearth.net/REST/v1/Routes/Driving?wp.0={origin}&wp.1={destination}&key={BING_MAPS_API_KEY}"
        
        # Make request to Bing Maps API
        response = requests.get(url)
        data = response.json()

        # Extract route details
        resource_sets = data.get('resourceSets', [])
        if resource_sets:
            resources = resource_sets[0].get('resources', [])
            if resources:
                route_data = resources[0]
                total_distance += route_data['travelDistance']
                total_toll_charges += route_data.get('tolls', 0)
                total_time += route_data['travelDuration']
                time1.append(str(timedelta(seconds=route_data['travelDuration'])))

    # Convert total time to hh:mm:ss format
    total_time_formatted = str(timedelta(seconds=total_time))

    return total_distance, total_toll_charges, total_time_formatted , time1


def parse_and_format_times(destinations_times):
    arrival_times = []
    for t in destinations_times:
        # Remove the surrounding quotes and convert to datetime object
        dt_str = t.strip('"')
        dt = eval(dt_str)

        # Format the datetime object to the desired format
        formatted_time = dt.strftime("%d %B %Y %H:%M:%S")
        arrival_times.append(formatted_time)

    return arrival_times

def total_diesel_cost(distance_matrix):
    total_distance = np.sum(distance_matrix)
    total_liters = total_distance / TRUCK_MILEAGE
    total_cost = total_liters * DIESEL_COST_PER_LITER
    return total_cost

def calculate_charges(route):
    url = "https://apis.tollguru.com/toll/v2/origin-destination-waypoints/"
    payload = {
        "from": {
            "address": route[0],
            "lat": locations1[route[0]][0],
            "lng": locations1[route[0]][1]
        },
        "to": {
            "address": route[-1],
            "lat": locations1[route[-1]][0],
            "lng": locations1[route[-1]][1]
        },
        "waypoints": [{"address": location} for location in route[1:-1]],
        "serviceProvider": "here",
        "vehicle": {
            "type": "2AxlesTruck",
            "weight": {
                "value": 20,
                "unit": "ton"
            },
            "height": {
                "value": 2.5,
                "unit": "meter"
            },
            "length": {
                "value": 7.5,
                "unit": "meter"
            },
            "axles": 2,
            "emissionClass": "euro_5"
        },
        "departure_time": 1609507347,
        "fuelOptions": {
            "fuelCost": {
                "value": 3.56,
                "units": "USD/gallon",
                "currency": "USD",
                "fuelUnit": "gallon"
            },
            "fuelEfficiency": {
                "city": 8,
                "hwy": 12,
                "units": "km/l"
            }
        },
        "units": {"currency": "INR"}
    }
    headers = {
        "content-type": "application/json",
        "x-api-key": "373gB8f3MBBMTgt2pRjd8fgNMFBH76Jg"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        fuel_cost = data['routes'][0]['costs']['fuel']
        toll_cost = data['routes'][0]['costs']['minimumTollCost']
        return fuel_cost, toll_cost
    except Exception as e:
        pass


def calculate_distance(route, distance_matrix):
    total_distance = 0
    for i in range(len(route) - 1):
        origin = route[i]
        destination = route[i + 1]
        total_distance += distance_matrix[origin][destination]
    return total_distance

options = list(locations1.keys())

selected_options = searchable_multiselect("Select or type options:", options)

# Initialize an empty dictionary to store the selected locations
locations = {}

# Loop through the selected city names
for city_name in selected_options:
    # Fetch the latitude and longitude values from the locations dictionary
    latitude, longitude = locations1.get(city_name, (None, None))
    # Store the latitude and longitude values in the location1 dictionary
    locations[city_name] = (latitude, longitude)

if st.button("Submit"):
    #st.write("You selected:", selected_options)
    
    distance_matrix = calculate_distance_matrix(locations, BING_MAPS_API_KEY)
    # Optimize routes
    routes = optimize_routes(locations, TRUCK_CAPACITY, distance_matrix)
    # Print routes
    for i, route in enumerate(routes):
        st.write(f"Truck Route:", " -> ".join(route))

    total_distance, total_toll_charges, total_time , time1= calculate_route_metrics(route)

    arrival_time = calculate_arrival_times(time1)

    st.write("Total Distance:", total_distance, "km")
    # Print the formatted arrival times for each destination
    for i, arrival_time in enumerate(arrival_time):
        st.write(f"Destination {i + 1} estimated arrival time:", arrival_time)
    st.write("Total Time:", total_time)
    try:
        fcost,tcost = calculate_charges(route)
        st.write("Total Fuel + Misc Cost = ",fcost)
        st.write("Total Toll Cost = ",tcost)
    except:
        pass
    

try:
    locations2 =  {}
    for city_name in route:
        # Fetch the latitude and longitude values from the locations dictionary
        latitude, longitude = locations1.get(city_name, (None, None))
        # Store the latitude and longitude values in the location1 dictionary
        locations2[city_name] = (latitude, longitude)


    # Create a folium map centered at the first location
    first_location = list(locations2.values())[0][:2]
    mymap = folium.Map(location=[22.3511148, 78.6677428], zoom_start=5)
    #st.write(locations2)
    print(locations2)
    # Function to add marker and polyline between two points
    def add_marker_and_route(start, end):
        # Generate the URL for OSRM API
        url = f'https://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?geometries=geojson'
        # Fetch route data from OSRM API
        response = requests.get(url)
        data = response.json()
        # Extract route coordinates
        route_coords = [[coord[1], coord[0]] for coord in data['routes'][0]['geometry']['coordinates']]
        # Add marker and polyline to the map without popup
        folium.Marker(end[:2]).add_to(mymap)
        folium.PolyLine(locations=route_coords, color='blue').add_to(mymap)
    # Iterate over locations and add markers and routes
    previous_location = None
    for i, (city, coords) in enumerate(locations2.items()):
        if i == len(locations2) - 1:
            break
        next_city = list(locations2.items())[i+1]
        # Add marker for each location
        folium.Marker(coords[:2]).add_to(mymap)
        # Add route between current and next locations
        add_marker_and_route(coords, next_city[1])

    # Save the map to an HTML file
    mymap.save('map.html')
    # Read the HTML file
    with open('map.html', 'r') as file:
        html_content = file.read()

    # Display the HTML content
    st.components.v1.html(html_content, width=800, height=600)

except:
    pass
