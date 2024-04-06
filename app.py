import streamlit as st
import numpy as np
import pandas as pd
import requests
from datetime import timedelta



import requests
import numpy as np

# Constants
BING_MAPS_API_KEY = "AvyY7OGE3G5E6Y7rdLxsEXTsAb89nxSGNmtVLWf5OXgxF61xZPlWGRF6fXtirFf0"
TRUCK_CAPACITY = 1000  # Assuming truck capacity in terms of product units
SALARY_PER_HOUR = 500  # Salary of driver per hour in rupees
TRUCK_MILEAGE = 5  # Truck mileage in kilometers per liter
DIESEL_COST_PER_LITER = 100  # Cost of diesel per liter in rupees
NUM_TRUCKS = 1  # Number of trucks

# Locations (latitude, longitude, diesel price per liter) - Example
df = pd.read_csv('cities.csv')
locations = {}

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    city_name = row['City']
    latitude = row['Lat']
    longitude = row['Long']
    locations[city_name] = (latitude, longitude)


# Calculate distance matrix using Bing Maps API
def calculate_distance_matrix(locations, api_key):
    distance_matrix = np.zeros((len(locations), len(locations)))
    for i, origin in enumerate(locations):
        for j, destination in enumerate(locations):
            if origin != destination:
                url = f"http://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?key={api_key}&origins={locations[origin][0]},{locations[origin][1]}&destinations={locations[destination][0]},{locations[destination][1]}&travelMode=driving"
                response = requests.get(url)
                data = response.json()
                if 'resourceSets' in data and data['resourceSets'] and 'resources' in data['resourceSets'][0] and data['resourceSets'][0]['resources'] and 'results' in data['resourceSets'][0]['resources'][0]:
                    distance_matrix[i][j] = data['resourceSets'][0]['resources'][0]['results'][0]['travelDistance']
                else:
                    print("Error retrieving distance data for", origin, "->", destination)
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
        nearest = min(unvisited, key=lambda x: distances[x])
        path.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    return path

# Optimize route using 2-opt
def optimize_route(route, distances):
    best_route = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route)):
                if j - i == 1:
                    continue
                new_route = route[:]
                new_route[i:j + 1] = route[j:i - 1:-1]
                if total_distance(new_route, distances) < total_distance(best_route, distances):
                    best_route = new_route
                    improved = True
        route = best_route
    return route

# Calculate total distance of a route
def total_distance(route, distances):
    total = 0
    for i in range(len(route) - 1):
        total += distances[route[i]][route[i+1]]
    return total

# Calculate total hours required for the journey
def total_hours(distance_matrix):
    total_distance = np.sum(distance_matrix)
    total_hours = total_distance / TRUCK_MILEAGE  # Assuming constant speed
    return total_hours

# Calculate total cost for diesel
def total_diesel_cost(distance_matrix):
    total_distance = np.sum(distance_matrix)
    total_liters = total_distance / TRUCK_MILEAGE
    total_cost = total_liters * DIESEL_COST_PER_LITER
    return total_cost

# Solve the optimization problem
def optimize_routes(locations, truck_capacity, distance_matrix):
    routes = []
    for i in range(NUM_TRUCKS):
        if i == 0:
            start_location = 'Bangalore'
        else:
            start_location = routes[i - 1][-1]
        remaining_locations = list(locations.keys())
        remaining_locations.remove(start_location)
        path = nearest_neighbor(distance_matrix[list(locations.keys()).index(start_location)])
        path = optimize_route(path, distance_matrix)
        routes.append([start_location] + [list(locations.keys())[i] for i in path])
    return routes

st.title("ALL_IN_RED")
st.subheader("Navigation for the real world")

def searchable_multiselect(label, options):
    selected_options = st.multiselect(label, options)
    if "Type here..." in selected_options:
        custom_option = st.text_input("Enter custom value:")
        if custom_option:
            selected_options.append(custom_option)
    return selected_options

options = list(locations.keys())

selected_options = searchable_multiselect("Select or type options:", options)

if selected_options:
    st.write("You selected:", selected_options)

    # Calculate distance matrix
distance_matrix = calculate_distance_matrix(locations, BING_MAPS_API_KEY)

    # Optimize routes
routes = optimize_routes(locations, TRUCK_CAPACITY, distance_matrix)

    # Print routes
for i, route in enumerate(routes):
    st.write(f"Truck {i+1} Route:", " -> ".join(route))

    # Calculate and print total hours required for the journey
    # total_hours_required = total_hours(distance_matrix)
    # print("Total hours required for the journey:", total_hours_required)

    # Calculate and print total diesel cost
    #total_diesel_cost = total_diesel_cost(distance_matrix)
    #print("Total diesel cost:", total_diesel_cost)

    # Print total distance
    # #total_distance = np.sum(distance_matrix)
    # print("Total distance to be traveled:", total_distance)
    
    # # Print distance matrix
    # print("Distance Matrix:")
    # print(distance_matrix)



