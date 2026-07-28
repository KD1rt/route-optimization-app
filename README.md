# Route Optimization Web Application

https://img.shields.io/badge/Python-3.11-blue
https://img.shields.io/badge/Flask-Web%20Application-black
https://img.shields.io/badge/Pandas-Data%20Processing-purple
https://img.shields.io/badge/OpenRouteService-Route%20Optimization-green

A Flask-based route optimization application that automates field routing workflows using the OpenRouteService Geocoding and Optimization APIs.

Designed for field operations, environmental consulting, and service-based workflows, the application takes a CSV of client locations, geocodes addresses, generates an optimized travel sequence, and exports a route schedule for daily operations.

---

## Table of Contents

- #overview
- #key-features
- #tech-stack
- #how-it-works
- #input-requirements
- [installation
- #usage
- [skills-demonstrated
- #future-improvements
- [License](#--

## Overview

Manual route planning can be time-consuming and inefficient when managing multiple client visits in a single day.

This application automates the process by:

- Validating uploaded client data
- Cleaning and standardizing addresses
- Geocoding locations
- Optimizing travel routes
- Automating laboratory drop-off logic for sample collection projects
- Exporting final route schedules to CSV

The goal was to create a practical tool that combines Python, geospatial analysis, API integration, and web development to solve a real operational problem.

---

## Key Features

✅ CSV upload through a web interface

✅ Address cleaning and validation

✅ OpenRouteService geocoding integration

✅ Multi-stop route optimization

✅ Automatic sample site identification

✅ Automated laboratory stop insertion

✅ Return-to-origin routing

✅ CSV export of optimized routes

✅ Error handling for invalid locations and missing data

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core application logic |
| Flask | Web application framework |
| Pandas | Data processing |
| Requests | API communication |
| OpenRouteService API | Geocoding and route optimization |

---

## How It Works

### 1. Upload Location Data

The user uploads a CSV containing client locations.

### 2. Validate Data

The application verifies required fields and removes invalid records.

### 3. Clean Addresses

Addresses are standardized to improve geocoding accuracy.

### 4. Geocode Locations

Addresses are converted into geographic coordinates using the OpenRouteService Geocoding API.

### 5. Optimize Route

The OpenRouteService Optimization API generates the most efficient travel sequence.

### 6. Apply Business Logic

Locations containing laboratory sample information are flagged.

If sample locations exist:

- The optimized route is generated
- A laboratory stop is automatically added
- The route returns to the starting location

### 7. Export Results

Users receive:

- An optimized route displayed in the browser
- A downloadable CSV route schedule

---

## Input Requirements

The application expects a CSV containing the following fields:

```text
Address
Lab Category #
Client
```

Example:

```csv
Address,Lab Category #,Client
123 Main Street Raleigh NC,,ABC Company
456 Oak Road Cary NC,WATER,XYZ Industries
789 Pine Avenue Durham NC,,Example Client
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/route-optimization-app.git

cd route-optimization-app
```

### Install Dependencies

```bash
pip install flask pandas requests
```

### Configure OpenRouteService API Key

#### Windows

```powershell
set ORS_API_KEY=YOUR_API_KEY
```

#### Mac/Linux

```bash
export ORS_API_KEY=YOUR_API_KEY
```

---

## Usage

Run the application:

```bash
python app.py
```

Navigate to:

```text
http://127.0.0.1:5000
```

Upload a CSV, enter a starting address, and generate an optimized route.

---

## Skills Demonstrated

This project highlights experience in:

- Python development
- Flask web applications
- REST API integration
- Geospatial data processing
- Route optimization workflows
- Data cleaning and validation
- CSV data automation
- Real-world GIS applications

---

## Future Improvements

- Interactive route map visualization
- Travel time and mileage reporting
- Multi-vehicle optimization
- PDF route reports
- User authentication
- Historical route storage
- GIS dashboard integration

---

## Project Motivation

As part of my ongoing work in Geographic Information Science and Technology (GIST), I wanted to build a practical application that applied geospatial analysis to a real business workflow.

Rather than focusing solely on mapping locations, this project demonstrates how GIS, Python, and web technologies can be combined to automate operational decision-making and improve field efficiency.

---

## License

This project is licensed under the MIT License.
