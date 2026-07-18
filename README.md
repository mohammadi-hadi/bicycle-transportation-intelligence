<div align="center">

# Bicycle Transportation Intelligence Dashboard

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io/)

*Streamlit operations dashboard for a city bike-sharing system — station alarms, rebalancing, geofencing, and idle-bike collection.*

</div>

## Overview

This project was built for the day-to-day operations of a city bike-share service. It reads current lock (bike), parking station, and trip data from the operator's Oracle database and presents four operational views in a Streamlit app:

- **Parking alarms** — flags stations whose bike count falls below or above configurable thresholds.
- **Rebalancing suggestions** — ranks stations by how many bikes should be dispatched to or collected from them.
- **Out-of-zone bikes** — uses geofencing (point-in-polygon tests with a buffer) to count and list bikes outside the allowed service area.
- **Collection suggestions** — maps bikes with no trips in the last 24 hours on an H3 hexagon choropleth so idle bikes can be collected.

## Data

Live data is pulled from the operator's Oracle database (lock, parking station, and trip tables); no data files are included in this repository. Database credentials are supplied through environment variables (see Quick Start) and are not part of the code.

## Methods

- **Database access**: `cx_Oracle` with `pandas.read_sql` queries against the lock, parking, and trip tables.
- **Geospatial logic**: `geopandas` and `shapely` handle the service-area polygon, buffering, and point-in-polygon checks; coordinates are bounded to the city area defined at the top of the script.
- **Hexagon aggregation**: `h3` bins bike locations into hexagons, rendered as `folium` choropleth and heat maps embedded in the Streamlit page.
- **Scaling**: `scikit-learn`'s `MinMaxScaler` normalizes station metrics for the alarm and rebalancing logic.
- **Localization**: the user interface labels are in Persian, matching the deployment context.

## Quick Start

The app requires access to the operator's Oracle database, so it will not run as-is outside that environment. To adapt it:

```bash
git clone https://github.com/mohammadi-hadi/bicycle-transportation-intelligence.git
cd bicycle-transportation-intelligence
pip install -r requirements.txt

# Required environment variables (values are not included in this repository)
export ORACLE_USER=...       # Oracle database user
export ORACLE_PASSWORD=...   # Oracle database password
export ORACLE_DSN=...        # Oracle DSN, e.g. host:port/service

streamlit run "Bicycle transportation intelligentization project.py"
```

The script also expects an Oracle Instant Client installation (it sets `ORACLE_HOME` in `oracle_connect()`). Update the city coordinate bounds (`city_lat1/2`, `city_long1/2`) for your own deployment.

## Repository Structure

```
bicycle-transportation-intelligence/
├── Bicycle transportation intelligentization project.py   # Streamlit app (all logic)
├── requirements.txt                                       # Python dependencies
├── CONTRIBUTING.md                                        # Contribution guidelines
├── LICENSE                                                # MIT License
└── README.md                                              # This file
```

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Contact

- **Hadi Mohammadi** — Utrecht University
- Website: [mohammadi.cv](https://mohammadi.cv)
