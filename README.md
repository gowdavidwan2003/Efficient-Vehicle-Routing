# ALL_IN_RED

**ALL_IN_RED - Navigation for the Real World**

---
[DEMO](https://smart-route.streamlit.app/)


**Overview:**

ALL_IN_RED is a streamlined navigation system designed to optimize truck routes for efficient delivery of goods. Leveraging data from various sources, including the Bing Maps API and the TollGuru API, this system calculates the most cost-effective and time-efficient routes for trucks based on factors such as distance, toll charges, and fuel costs. It also incorporates quantum annealing techniques to solve complex optimization problems, ensuring that routes are optimized to minimize overall travel time and expenses.

---

**Features:**

1. **Dynamic Route Optimization:** ALL_IN_RED dynamically optimizes truck routes based on real-time data, ensuring that deliveries are made via the most efficient paths.

2. **Cost Estimation:** The system provides accurate estimates of total travel distance, toll charges, fuel costs, and total travel time, allowing businesses to plan their logistics operations more effectively.

3. **Quantum Annealing:** By leveraging quantum annealing techniques, ALL_IN_RED solves complex optimization problems to find the shortest and most efficient routes, even in scenarios with multiple waypoints and constraints.

4. **Interactive Map Visualization:** The system includes an interactive map visualization feature, powered by the Folium library, which displays the optimized truck routes along with markers for each destination.

---

**Usage:**

To use ALL_IN_RED, follow these steps:

1. **Select Destinations:** Choose the destinations for the truck routes by selecting from the available options.

2. **View Optimized Routes:** The system will display the optimized routes for the selected destinations, along with estimated travel distance, toll charges, fuel costs, and total travel time.

3. **Interactive Map:** Explore the optimized routes visually on the interactive map, which displays the truck routes and destination markers.

---

**Dependencies:**

ALL_IN_RED relies on the following dependencies:

- Streamlit
- Pandas
- NumPy
- Requests
- Folium
- DWave (for quantum annealing)
- Graphviz (for visualization)
- OSRM (Open Source Routing Machine)

---

**Installation:**

To install ALL_IN_RED and its dependencies, follow these steps:

1. Install Python (if not already installed).
2. Install Streamlit using pip: `pip install streamlit`
3. Install the required Python libraries listed above using pip.

---

**Usage Example:**

```python
# Run the Streamlit app
streamlit run all_in_red.py
```

---

**Contributors:**

- Vidwan Gowda H M  (1MS21IS126)
- Adithya Narayana Holla (1MS21AI004)

---

**License:**

This project is licensed under the MIT License. See the LICENSE file for more details.

---

**Contact:**

For questions or inquiries, please contact Vidwan Gowda H M at gowdavidwan2003@gmail.com
