"""
Flask Route Optimization Web Application
"""

import sys
from flask import Flask, render_template, request
import pandas as pd
import requests
import os

# This function below would be used to utilize the render template
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        file = request.files['file']
        start_address = request.form['start_address'] # Starting address from user input
        user_response = request.form['user_response'] # User response from form
        try:
            optimized_data = optimize_route(file, start_address, user_response)
            return render_template(
                'results.html',  # template name
                tables=[optimized_data.to_html(classes='data', index=False)],  # context data
                titles=optimized_data.columns.values
                )

        except ValueError as e:
            return f"<h1>Error</h1><p>{str(e)}</p><br><a href='/'>Go Back</a>"
        except Exception as e:
            return f"<h1>Unexpected Error</h1><p>{str(e)}</p><br><a href='/'>Go Back</a>"
    return render_template('index.html')

# Function to optimize route using ORS API
def optimize_route(file, start_address, user_response):
    # Set API
    api_key = os.getenv('ORS_API_KEY')
    if not api_key:
        raise ValueError("ORS_API_KEY environment variable not set")
    api_url = 'https://api.openrouteservice.org/optimization'
    api_geocode_url = 'https://api.openrouteservice.org/geocode/search'
    
    def clean_address(address):
        address = str(address).strip()
        while '  ' in address:
            address = address.replace('  ', ' ')
        while ',,' in address:
            address = address.replace(',,', ',')
        if '-' in address:
            address_parts = address.split('-', 1)
            address = address_parts[1].strip()
            address = address.replace('/', ' ')
        address_replacements = {
            ' St.': ' Street',
            ' Rd.': ' Road',
            ' Ave.': ' Avenue',
            ' Blvd.': ' Boulevard',
            ' Dr.': ' Drive',
            ' Ln.': ' Lane',
            ' Ct.': ' Court',
            ' Pl.': ' Place'
        }
        for old, new in address_replacements.items():
            address = address.replace(old, new)
        
        # clean up the extra spaces
        while '  ' in address:
            address = address.replace('  ', ' ')
        return address.strip()
    
    # Set geocoding function
    def geocode_address(address, api_key):
        if not address or address.strip() == '':
            return None
        params = {
            'api_key': api_key,
            'text': address,
        }
        response = requests.get(api_geocode_url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get("features"):
                coords = data["features"][0]["geometry"]["coordinates"]
                return coords[1], coords[0]  # Return as (lat, lon)
        return None
    
    # Create function to find location details by job id variable
    def find_location_by_id(job_id, locations):
        for loc in locations:
            if loc['job_id'] == job_id:
                return loc
        return None
    # PHASE 1: Read and clean data
    print(" PHASE 1: Reading and Cleaning Data ")
   
    df = pd.read_csv(file)
    print("CSV file read successfully.")
    print(f'Total rows in CSV file: {len(df)}')
    
    # Normalize column names (collapse multiple spaces)
    df.columns = [" ".join(c.strip().split()) for c in df.columns]

    # Required columns check
    required_columns = ['Address', 'Lab Category  #', 'Client']
    if not set(required_columns).issubset(df.columns):
        missing_columns = set(required_columns) - set(df.columns)
        raise ValueError(f"Missing required columns: {missing_columns}")


    print(f"All required columns are present: {required_columns}")

    # Filter out rows with missing address
    original_row_count = len(df)
    df = df[df['Address'].notna() & (df['Address'].str.strip() != '')]
    filtered_row_count = len(df)
    print(f"Filtered address: {filtered_row_count} rows remaining out of {original_row_count}")

    # PHASE 2: Geocode Addresses
    print(" PHASE 2: Geocoding Addresses ")

    location_data = []
    failed_location_data = []

    for index, row in df.iterrows():
        raw_address = str(row['Address'])  # FIXED: Convert to string first
        if raw_address.lower() == 'nan' or raw_address.strip() == '':
            continue

        client = row["Client"]
        lab_category_value = row["Lab Category  #"]

        address = clean_address(raw_address)
        # Identify if sample or not
        lab_category = None
        is_sample = False
        if pd.notna(lab_category_value) and str(lab_category_value).strip() != '':
            lab_category = str(lab_category_value).strip()
            is_sample = True
        
        coords = geocode_address(address, api_key)
        if coords:
            latitude, longitude = coords
            location_package = {
                "job_id": index + 1,
                "Address" : address,
                "Client": client,
                "is_sample": is_sample,
                "lab_category": lab_category if lab_category else "",
                "latitude": latitude,
                "longitude": longitude
            }
            location_data.append(location_package)
            print(f" Successfully geocoded: {address} -> ({latitude}, {longitude}) ")
        else:
            print(f" Failed to geocode address: {address} ")
            failed_location_data.append({
                "Client": client,
                "Address": address
            })
    print(f"Total successfully geocoded locations: {len(location_data)}")

    if failed_location_data:
        print("The following addresses could not be geocoded:")
        for failed in failed_location_data:
            print(f" - {failed['Address']} (Client: {failed['Client']})")
    # Validate that there are enough locations to optimize
    if len(location_data)<2:
        raise ValueError("Not enough valid locations to optimize the route. Please check the addresses provided.")
    
    # PHASE 3: Prepare optimization request
    print(" PHASE 3: Preparing Optimization Request ")
    sample_list = [loc for loc in location_data if loc['is_sample']]
    non_sample_list = [loc for loc in location_data if not loc['is_sample']]

    # Optimal route locations list
    optimal_job_order = non_sample_list + sample_list

    # Reassign job IDs
    for index, loc in enumerate(optimal_job_order):
        loc['job_id'] = index + 1
    print(f" Non_sample locations: {len(non_sample_list)} ")
    print(f" Sample locations: {len(sample_list)} ")
    print(f"Total stops to optimize: {len(optimal_job_order)}")

    # PHASE 4: Optimize with ORS API
    print(" PHASE 4: Optimizing Route with ORS API ")
    # Geocode starting address
    start_add = clean_address(start_address)
    print(f"Geocoding starting address: {start_add}")

    start_coords = geocode_address(start_add, api_key)
    if not start_coords:
        error_message = f"Could not geocode starting address: {start_add}"
        print(f"{error_message}")
        raise ValueError(error_message)
    
    start_lat, start_lon = start_coords
    print(f"Starting address geocoded to: ({start_lat}, {start_lon})")
    
    start_location = {
        "Address": start_add,
        "Client": "START",
        "latitude": start_lat,
        "longitude": start_lon
    }

    # If there are sample sites, add the lab as final stop before returning to start
    lab_stop = None
    if sample_list:
        lab_stop = {
            "Address": "104 Woodwinds Industrial Ct Suite A, Cary, NC 27511",
            "Client": "Eurofins Lab",
            "latitude": 35.761890,
            "longitude": -78.818657
        }
        print("Adding Eurofins Lab as final stop before returning to start.")
    
    jobs = [{"id": loc["job_id"], "location": [loc["longitude"], loc["latitude"]]} for loc in optimal_job_order]

    vehicles = [{
        "id": 1,
        "profile": "driving-car",
        "start": [start_lon, start_lat],
        "end": [start_lon, start_lat]
    }]

    payload = {
        "jobs": jobs,
        "vehicles": vehicles,
        "options": {"g": True}
    }

    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    # Make the optimization request
    print("Calling ORS Optimization API...")
    response = requests.post(api_url, json=payload, headers=headers)
    print(f"ORS API response status code: {response.status_code}")

    if response.status_code != 200:
        api_error = f"API request failed with status code {response.status_code}: {response.text}"
        print(api_error)
        raise ValueError(api_error)
    
    optimization_result = response.json()
    route = optimization_result.get('routes', [])[0] if 'routes' in optimization_result else None

    if not route:
        raise ValueError("No route found in optimization result.")
    
    print("Optimization successful. Processing results...")

    # Phase 5: Process and return results

    print(" PHASE 5: Processing and Returning Results ")
    optimized_order = []
    stop_counter = 0

    optimized_order.append({
        "Stop Number": "Start Location",
        "Client": start_location["Client"],
        "Address": start_location["Address"],
        "Is Sample": "No",
        "Lab Category": "",
    })
    print(f" {start_location['Address']}")

    # Process each stop in the optimized route
    for step in route['steps']:
        if step['type'] == 'job':
            job_id = step['job']
            matched_location = find_location_by_id(job_id, optimal_job_order)
            if matched_location:
                stop_counter += 1  # FIXED: Increment BEFORE adding to list
                optimized_order.append({
                    "Stop Number": f"Stop {stop_counter}",
                    "Client": matched_location["Client"],
                    "Address": matched_location["Address"],
                    "Is Sample": "Yes" if matched_location["is_sample"] else "No",
                    "Lab Category": matched_location.get("lab_category", ""),
                })
                print(f" Stop {stop_counter}: {matched_location['Address']} (Sample: {'Yes' if matched_location['is_sample'] else 'No'})")
    
    if lab_stop:
        stop_counter += 1  # FIXED: Increment counter for lab stop too
        optimized_order.append({
            "Stop Number": f"Stop {stop_counter}",
            "Client": lab_stop["Client"],
            "Address": lab_stop["Address"],
            "Is Sample": "No",
            "Lab Category": "",
        })
        print(f" Stop {stop_counter}: {lab_stop['Address']} (Sample: No)")
    
    # Add return to start location
    optimized_order.append({
        "Stop Number": "End Location",
        "Client": start_location["Client"],
        "Address": start_location["Address"],
        "Is Sample": "No",
        "Lab Category": "",
    })
    print(f" Return to: {start_location['Address']}")

    # PHASE 6: Save and export results
    print(" PHASE 6: Saving and Exporting Results ")
    csv_filename = user_response + '_optimized_route.csv'
    result_df = pd.DataFrame(optimized_order)
    result_df.to_csv(csv_filename, index=False)
    print(f"Optimized route saved to {csv_filename}")
    print(f"Total stops in optimized route: {stop_counter}")
    return result_df

# PHASE 7: RUN APPLICATION with Flask
if __name__ == '__main__':
    print("Flask Route Optimization Application Starting...")
    print("Starting Server")
    print("Access the application at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

