# Bicycle Transportation Intelligence

A Streamlit operations dashboard for a bike-sharing system, combining live Oracle database queries with geospatial analysis of bikes, parking stations, and trips.

## Overview

This project was built for the day-to-day operations of a city bike-share service. It reads current lock (bike), parking station, and trip data from the operator's Oracle database and presents four operational views in a Streamlit app:

- **Parking alarms** — flags stations whose bike count falls below or above configurable thresholds.
- **Rebalancing suggestions** — ranks stations by how many bikes should be dispatched to or collected from them.
- **Out-of-zone bikes** — uses geofencing (point-in-polygon tests with a buffer) to count and list bikes outside the allowed service area.
- **Collection suggestions** — maps bikes with no trips in the last 24 hours on an H3 hexagon choropleth so idle bikes can be collected.

## Data / Methods

- Live data is pulled with `cx_Oracle` and `pandas.read_sql` from the operator's lock, parking, and trip tables.
- `geopandas` and `shapely` handle the service-area polygon, buffering, and point-in-polygon checks; coordinates are bounded to the city area defined at the top of the script.
- `h3` aggregates bike locations into hexagonal bins, rendered as `folium` choropleth and heat maps embedded in the Streamlit page.
- `scikit-learn`'s `MinMaxScaler` normalizes station metrics for the alarm and rebalancing logic.
- The user interface labels are in Persian, matching the deployment context.

## Repository structure

```
Bicycle-transportation-intelligence-/
├── Bicycle transportation intelligentization project.py   # Streamlit app (all logic)
├── CONTRIBUTING.md                                        # Contribution guidelines
├── LICENSE                                                # MIT License
└── README.md                                              # This file
```

## How to run

The app requires access to the operator's Oracle database, so it will not run as-is outside that environment. To adapt it:

```bash
pip install pandas numpy geopandas shapely streamlit scikit-learn cx_Oracle folium h3 osmnx branca

streamlit run "Bicycle transportation intelligentization project.py"
```

Update the Oracle connection settings in `oracle_connect()` and the city coordinate bounds (`city_lat1/2`, `city_long1/2`) for your own deployment.

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
