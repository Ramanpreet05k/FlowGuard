import pandas as pd
import numpy as np
import os
from datetime import datetime

# Define file paths relative to the backend directory
RAW_DATA_PATH = 'data/raw_violations.csv'
EXPORT_DATA_PATH = 'data/flowguard_processed_top_5k.csv'

def process_data():
    print("🚀 Initializing FlowGuard Data Pipeline...")
    
    # 1. PRE-FLIGHT CHECK
    if not os.path.exists(RAW_DATA_PATH):
        print(f"❌ Error: Could not find {RAW_DATA_PATH}")
        print("Please ensure your hackathon dataset is named 'raw_violations.csv' and placed in the 'backend/data/' folder.")
        return

    # 2. LOAD DATA
    print("Loading raw dataset...")
    df = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    print(f"Loaded {len(df)} raw rows.")

    # Standardize column names (lowercase, strip whitespace) to prevent key errors
    df.columns = df.columns.str.strip().str.lower()

    # 3. CLEANING & FILTERING
    # Ensure critical columns exist before proceeding
    required_cols = ['validation_status', 'latitude', 'longitude', 'vehicle_type', 'created_datetime']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"❌ Error: Dataset is missing required columns: {missing_cols}")
        return

    # Drop rejected tickets and missing coordinates
    df = df[df['validation_status'].astype(str).str.lower() == 'approved']
    df = df.dropna(subset=['latitude', 'longitude', 'vehicle_type', 'created_datetime'])
    print(f"Retained {len(df)} valid, approved rows after cleaning.")

    # 4. TIME-TO-CLEARANCE CALCULATION
    print("Calculating temporal metrics...")
    
    # Force both datetime columns into the exact same timezone (UTC) to prevent subtraction errors
    df['created_datetime'] = pd.to_datetime(df['created_datetime'], errors='coerce', utc=True)
    
    # Handle cases where 'closed_datetime' might not exist or is empty
    if 'closed_datetime' in df.columns:
        df['closed_datetime'] = pd.to_datetime(df['closed_datetime'], errors='coerce', utc=True)
        df['hours_blocked'] = (df['closed_datetime'] - df['created_datetime']).dt.total_seconds() / 3600
        # If no closed time, assume it is currently active and apply a standard 3-hour penalty
        df['hours_blocked'] = df['hours_blocked'].fillna(3.0) 
    else:
        df['hours_blocked'] = 3.0

    # Remove negative times (likely data entry errors in the raw dataset)
    df = df[df['hours_blocked'] >= 0]

    # 5. CONGESTION IMPACT SCORE (CIS) ENGINE
    print("⚙️ Calculating Dynamic CIS Scores...")
    
    # A. Vehicle Weight Multiplier
    weight_map = {
        'TANKER': 5.0, 
        'TRUCK': 4.0, 
        'BUS': 4.0,
        'CAR': 2.0, 
        'AUTO': 1.5,
        'SCOOTER': 1.0, 
        'BIKE': 1.0
    }
    df['vehicle_weight'] = df['vehicle_type'].astype(str).str.upper().map(weight_map).fillna(1.5)

    # B. Time Multiplier (Punish rush hour violations heavily)
    def get_time_multiplier(dt):
        if pd.isnull(dt):
            return 1.0
        hour = dt.hour
        if 8 <= hour <= 11 or 17 <= hour <= 20:
            return 3.0  # Rush Hour
        elif hour >= 23 or hour <= 5:
            return 0.5  # Dead of night
        return 1.0

    df['time_multiplier'] = df['created_datetime'].apply(get_time_multiplier)

    # C. Location Criticality
    # If junction_name exists, heavily weight high-traffic zones
    if 'junction_name' in df.columns:
        high_traffic_junctions = ['BTP051 - Safina Plaza Junction', 'Silk Board', 'Majestic']
        df['location_criticality'] = np.where(
            df['junction_name'].isin(high_traffic_junctions), 2.5, 1.0
        )
    else:
        df['location_criticality'] = 1.0

    # D. Final CIS Calculation Equation
    df['CIS'] = df['vehicle_weight'] * df['time_multiplier'] * df['location_criticality'] * df['hours_blocked']

    # 6. SORT & EXPORT
    print("Optimizing and exporting dataset...")
    df = df.sort_values(by='CIS', ascending=False)

    # Extract the top 5,000 most critical violations for the prototype UI
    export_df = df.head(5000)
    
    # Ensure we only export columns that actually exist in the dataframe
    desired_columns = ['latitude', 'longitude', 'vehicle_type', 'junction_name', 'police_station', 'hours_blocked', 'CIS']
    final_columns = [col for col in desired_columns if col in export_df.columns]
    
    export_df = export_df[final_columns]

    # Save to the data folder
    os.makedirs(os.path.dirname(EXPORT_DATA_PATH), exist_ok=True)
    export_df.to_csv(EXPORT_DATA_PATH, index=False)
    
    print("✅ Pipeline Complete!")
    print(f"Highest calculated CIS Score: {export_df['CIS'].max():.2f}")
    print(f"Exported optimized dataset to: {EXPORT_DATA_PATH}")

if __name__ == "__main__":
    process_data()