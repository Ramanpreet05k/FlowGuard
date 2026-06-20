from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from math import radians, cos, sin, asin, sqrt

app = FastAPI(title="FlowGuard API", description="Predictive Dispatch & CIS Engine")

# Crucial: Allow the Next.js frontend (which will run on port 3000) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, change this to your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "data/flowguard_processed_top_5k.csv"

# --- HELPER FUNCTIONS ---

def haversine_distance(lon1, lat1, lon2, lat2):
    """Calculates the great-circle distance between two points on Earth in kilometers."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return c * r

def load_data():
    try:
        return pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Processed dataset not found. Run pipeline.py first.")

# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "FlowGuard Engine is active. Proceed to /docs for API testing."}

@app.get("/api/hotzones")
def get_clustered_hotzones():
    """
    Groups individual parking violations into severe 'Hotzones' using DBSCAN spatial clustering.
    Returns the center coordinates and total CIS score of each Hotzone.
    """
    df = load_data()
    
    # Extract coordinates for clustering
    coords = df[['latitude', 'longitude']].values
    
    # Run DBSCAN Clustering Algorithm
    # eps=0.005 is roughly a 500-meter radius. min_samples=3 means at least 3 vehicles make a cluster.
    db = DBSCAN(eps=0.005, min_samples=3).fit(coords)
    df['cluster'] = db.labels_
    
    hotzones = []
    
    # Group the data by the new clusters (Ignore label -1, which is "noise" or isolated vehicles)
    for cluster_id, group in df[df['cluster'] != -1].groupby('cluster'):
        center_lat = group['latitude'].mean()
        center_lon = group['longitude'].mean()
        total_cis = group['CIS'].sum()
        vehicle_count = len(group)
        
        hotzones.append({
            "id": int(cluster_id),
            "latitude": round(center_lat, 6),
            "longitude": round(center_lon, 6),
            "total_cis": round(total_cis, 2),
            "vehicle_count": int(vehicle_count)
        })
        
    # Sort hotzones by most critical (Highest CIS) first
    hotzones = sorted(hotzones, key=lambda x: x['total_cis'], reverse=True)
    return {"hotzones": hotzones}


@app.get("/api/routes")
def get_dispatch_route():
    """
    Generates an optimized patrol route for police to clear the highest CIS hotzones.
    Uses a Greedy Nearest-Neighbor approach for fast computation.
    """
    # 1. Get the current active hotzones
    hotzones_data = get_clustered_hotzones()["hotzones"]
    
    if not hotzones_data:
        return {"route": []}

    # 2. Grab the top 5 most critical hotzones to form today's patrol route
    critical_nodes = hotzones_data[:5]
    
    # 3. Simulate a Police Station Starting Point (Using the first hotzone as a proxy start for the prototype)
    # In a real app, you would pass the lat/lon of "Shivajinagar Police Station" here.
    start_node = critical_nodes.pop(0)
    
    optimized_route = [start_node]
    current_node = start_node
    
    # 4. Greedy Routing Algorithm: Always go to the closest critical hotzone next
    while critical_nodes:
        # Find the nearest unvisited node
        nearest_node = min(
            critical_nodes, 
            key=lambda x: haversine_distance(current_node['longitude'], current_node['latitude'], x['longitude'], x['latitude'])
        )
        optimized_route.append(nearest_node)
        critical_nodes.remove(nearest_node)
        current_node = nearest_node
        
    return {"optimized_route": optimized_route}