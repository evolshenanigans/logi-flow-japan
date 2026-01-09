import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# ---------------------------------------------------------
# 1. APP CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Logi-Flow Japan", layout="wide")

translations = {
    'en': {
        'title': "Logi-Flow Japan: 2024 Optimization",
        'sidebar_title': "Settings",
        'lang_select': "Language / 言語",
        'kpi_cargo': "Total Cargo (Tons)",
        'kpi_cost': "Est. Fuel Cost (¥)",
        'tab_demand': "Demand Forecast",
        'tab_route': "Route Optimization",
        'btn_solve': "🚀 Generate Optimized Routes",
        'route_res': "Optimization Results"
    },
    'jp': {
        'title': "Logi-Flow Japan: 2024年物流最適化",
        'sidebar_title': "設定",
        'lang_select': "Language / 言語",
        'kpi_cargo': "総貨物量 (トン)",
        'kpi_cost': "推定燃料費 (円)",
        'tab_demand': "需要予測",
        'tab_route': "ルート最適化",
        'btn_solve': "🚀 ルートを最適化する",
        'route_res': "最適化結果"
    }
}


st.sidebar.title("Logi-Flow Settings")
lang = st.sidebar.radio("Language / 言語", ('English', '日本語'))
current_lang = 'en' if lang == 'English' else 'jp'
t = translations[current_lang]

st.title(t['title'])

# ---------------------------------------------------------
# 2. THE OPTIMIZATION ENGINE (Backend)
# ---------------------------------------------------------

def create_data_model():
    """Creates the data for the VRP with Time Windows."""
    np.random.seed(42)
    data = {}
    center_lat = 35.68
    center_lon = 139.76
    data['locations'] = []
    for _ in range(20):
        lat = center_lat + random.uniform(-0.05, 0.05)
        lon = center_lon + random.uniform(-0.05, 0.05)
        data['locations'].append((lat, lon))
    data['num_vehicles'] = 4
    data['depot'] = 0
    data['service_time'] = 5 
    
    # RELAXED Time Windows (0-240 mins) to ensure a solution is found
    data['time_windows'] = [(0, 1000)] # Depot open all day
    for _ in range(19):
        start = np.random.randint(0, 500)
        end = start + 240 # Wide 4-hour window
        data['time_windows'].append((start, end))
        
    return data

def solve_vrp(data):
    """Solves the Vehicle Routing Problem."""
    
    manager = pywrapcp.RoutingIndexManager(len(data['locations']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)
    
    locations = data['locations']
    distance_matrix = {}
    for from_node in range(len(locations)):
        distance_matrix[from_node] = {}
        for to_node in range(len(locations)):
            if from_node == to_node:
                distance_matrix[from_node][to_node] = 0
            else:
                dist_km = geodesic(locations[from_node], locations[to_node]).km
                travel_time = (dist_km / 30) * 60
                distance_matrix[from_node][to_node] = int(travel_time)

    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node] + data['service_time']

    time_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(time_callback_index)

    routing.AddDimension(
        time_callback_index,
        1000,  # Max Waiting Time (Slack)
        2000,  # Max Work Time
        False,
        'Time'
    )
    time_dimension = routing.GetDimensionOrDie('Time')

    for location_idx, (start, end) in enumerate(data['time_windows']):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(start, end)

    time_dimension.SetGlobalSpanCostCoefficient(10)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.time_limit.seconds = 30 # Safety Timeout

    solution = routing.SolveWithParameters(search_parameters)
    return solution, manager, routing, time_dimension

# ---------------------------------------------------------
# 2.5 map data
# ---------------------------------------------------------

def create_map(data, manager, routing, solution):
    """Draws the routes on a Folium map."""
    
    depot_loc = data['locations'][data['depot']]
    m = folium.Map(location=depot_loc, zoom_start=13)
    
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred']
    
    # Draw Routes
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route_coords = []
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_coords.append(data['locations'][node_index])
            index = solution.Value(routing.NextVar(index))
            
        # Add the return to Depot
        node_index = manager.IndexToNode(index)
        route_coords.append(data['locations'][node_index])
        
        if len(route_coords) > 2:
            folium.PolyLine(
                route_coords, 
                color=colors[vehicle_id % len(colors)], 
                weight=5, 
                opacity=0.8,
                tooltip=f"Truck {vehicle_id}"
            ).add_to(m)
            
    for i, loc in enumerate(data['locations']):
        if i == data['depot']:
            folium.Marker(
                loc, 
                popup="Depot (Tokyo Station)", 
                icon=folium.Icon(color='black', icon='home')
            ).add_to(m)
        else:
            start, end = data['time_windows'][i]
            folium.Marker(
                loc, 
                popup=f"Customer {i} (Window: {start}-{end}m)", 
                icon=folium.Icon(color='blue', icon='user')
            ).add_to(m)
            
    return m

# ---------------------------------------------------------
# 3. UI & VISUALIZATION (Frontend)
# ---------------------------------------------------------

tab1, tab2 = st.tabs([t['tab_demand'], t['tab_route']])

# --- TAB 1: Demand Forecast (Original Logic) ---
with tab1:
    # Load Data
    @st.cache_data
    def load_data():
        return pd.read_parquet('data/features_engineered.parquet')

    df = load_data()

    # KPI Row
    c1, c2, c3 = st.columns(3)
    c1.metric(t['kpi_cargo'], f"{df['Cargo_Weight_Tons'].sum():,.0f}")
    c2.metric(t['kpi_cost'], "¥1,250,000", delta="-12%")
    c3.metric("Model Precision", "0.85 Tons")

    st.subheader("Cargo Volume by Prefecture")
    cargo_by_pref = df.groupby('Origin_Prefecture_Code')['Cargo_Weight_Tons'].sum().reset_index()
    fig = px.bar(cargo_by_pref, x='Origin_Prefecture_Code', y='Cargo_Weight_Tons')
    st.plotly_chart(fig)

# --- TAB 2: Route Optimization (Fixed with Session State) ---
with tab2:
    st.header(t['tab_route'])
    st.write("Constraint Programming Engine: **Google OR-Tools**")

    if 'solution_found' not in st.session_state:
        st.session_state.solution_found = False
    
    if st.button(t['btn_solve']):
        with st.spinner("Optimizing Routes..."):
            data = create_data_model()
            solution, manager, routing, time_dimension = solve_vrp(data)
            st.session_state.vrp_data = data
            st.session_state.vrp_solution = solution
            st.session_state.vrp_manager = manager
            st.session_state.vrp_routing = routing
            st.session_state.vrp_time_dim = time_dimension
            st.session_state.solution_found = True

    if st.session_state.solution_found:
        data = st.session_state.vrp_data
        solution = st.session_state.vrp_solution
        manager = st.session_state.vrp_manager
        routing = st.session_state.vrp_routing
        time_dimension = st.session_state.vrp_time_dim
        
        if solution:
            st.success(f"Optimization Complete! Total Time Cost: {solution.ObjectiveValue():.0f} min")
            
            st.subheader("🗺️ Operational Map")
            map_obj = create_map(data, manager, routing, solution)
            st_folium(map_obj, width=725)
            
            st.divider()
            st.subheader("📋 Route Manifest")
            for vehicle_id in range(data['num_vehicles']):
                index = routing.Start(vehicle_id)
                route_text = ""
                route_len = 0
                
                while not routing.IsEnd(index):
                    time_var = time_dimension.CumulVar(index)
                    arrival_time = solution.Min(time_var)
                    node = manager.IndexToNode(index)
                    
                    route_text += f"Stop {node} (@{arrival_time}m) ➝ "
                    index = solution.Value(routing.NextVar(index))
                    route_len += 1
                
                time_var = time_dimension.CumulVar(index)
                arrival_time = solution.Min(time_var)
                route_text += f"Depot (@{arrival_time}m)"
                
                if route_len > 0: 
                    st.markdown(f"**🚚 Truck {vehicle_id}**")
                    st.code(route_text)
                else:
                    st.caption(f"Truck {vehicle_id}: Not needed")
        else:
            st.error("No solution found. Constraints are too strict.")