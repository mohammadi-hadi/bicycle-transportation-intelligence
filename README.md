<div align="center">

# Bicycle Transportation Intelligence

### Geospatial Analysis for Smart Bike-Sharing Systems

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io/)

*Data-driven insights for urban bicycle transportation planning*

---

</div>

## Overview

This project provides geospatial analysis tools for intelligent bicycle transportation systems. It combines spatial data processing with real-time database integration to analyze cycling patterns and optimize bike-sharing operations.

## Features

- **Geospatial Analysis**: Process cycling routes and allowed areas using GeoPandas
- **Database Integration**: Real-time data retrieval from Oracle databases
- **Interactive Dashboard**: Streamlit-based visualization interface
- **Spatial Operations**: Buffer zones, polygon processing, and route analysis

## Technology Stack

- **GeoPandas**: Geospatial data manipulation
- **Shapely**: Geometric operations
- **Streamlit**: Interactive web dashboards
- **cx_Oracle**: Oracle database connectivity
- **scikit-learn**: Data preprocessing and normalization

## Quick Start

```bash
# Clone the repository
git clone https://github.com/mohammadi-hadi/Bicycle-transportation-intelligence-.git
cd Bicycle-transportation-intelligence-

# Install dependencies
pip install pandas numpy geopandas shapely streamlit scikit-learn cx_Oracle

# Run the application
streamlit run "Bicycle transportation intelligentization project.py"
```

## Configuration

The system is configured for a specific city area:
- Latitude range: 29.49° - 29.84°
- Longitude range: 52.39° - 52.68°

Modify the coordinate boundaries in the script to adapt for different regions.

## Repository Structure

```
Bicycle-transportation-intelligence-/
├── Bicycle transportation intelligentization project.py  # Main application
├── LICENSE                                               # MIT License
├── CONTRIBUTING.md                                       # Contribution guidelines
└── README.md                                            # This file
```

## Requirements

- Python 3.8+
- pandas
- numpy
- geopandas
- shapely
- streamlit
- cx_Oracle
- scikit-learn

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or collaboration inquiries:
- **Hadi Mohammadi** - Utrecht University
- **Email**: [h.mohammadi@uu.nl](mailto:h.mohammadi@uu.nl)
- **Website**: [mohammadi.cv](https://mohammadi.cv)
