# Vehicle Registration Dashboard

An interactive **Streamlit-based data visualization dashboard** for analyzing vehicle registration trends across manufacturers, fuel types, and states.  
It provides **growth analysis**, **market share insights**, and **EV adoption trends** with options to **export results to PDF**.

---

## Features

- **Dynamic Filters**
  - Filter by **Vehicle Category**, **Manufacturer**, **State**, and **Year Range**
  - Supports multiple selections

- **Interactive Visualizations**
  - Vehicle registration trends (monthly)
  - Market share by manufacturer (pie chart)
  - EV vs Non-EV registration trends
  - EV adoption percentage over time
  - Quarter-over-quarter & year-over-year growth trends

- **Automated Insights**
  - Highest EV adoption state
  - Fastest growing manufacturer (YoY)
  - Most popular fuel type
  - Largest drop in registrations
  - Most consistent growth manufacturer

- **Export to PDF**
  - Download **Dashboard Report (Charts + KPIs + Insights)**
  - Download **Full Filtered Data Table**

---

## Tech Stack

- **Python 3.x**
- **Streamlit** – Web app framework
- **Plotly** – Interactive charting
- **Pandas** – Data manipulation
- **ReportLab** – PDF generation

---

## Project Structure
```
vahan-dashboard/
│
├── main.py                # Main Streamlit application
├── data_utils.py          # Helper functions (growth calculations, etc.)
├── vehicle_data_big.csv   # Dataset
├── requirements.txt       # Dependencies
└── README.md              # Project documentation
```

---

## Dataset
The dataset contains:
- `Month` – Month of registration
- `Category` – Vehicle type (2W, 3W, 4W, etc.)
- `Manufacturer` – Brand name
- `State` – Registration state
- `FuelType` – Fuel category (Petrol, Diesel, Electric, etc.)
- `Registrations` – Number of vehicles registered
- `QoQ_Growth` – Quarter-over-quarter growth (%)
- `YoY_Growth` – Year-over-year growth (%)

---

## Installation & Setup

### Clone the repository
```bash
git clone https://github.com/rayyan-14/vahan-dashboard.git
cd vahan-dashboard
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the Streamlit app
```bash
streamlit run main.py
```

---

## Usage Guide

1. Open the app in your browser (Streamlit will auto-open on `http://localhost:8501`)
2. Select filters from the sidebar
3. View **interactive charts** & **KPIs**
4. Download:
   - **PDF Report with Charts & Insights**
   - **Full Data Table (PDF)**

---

## Example Insights Generated

- **Highest EV Adoption State:** Karnataka (42.3%)
- **Fastest Growing Manufacturer YoY:** Tata (+32.1%)
- **Most Popular Fuel Type:** Petrol (64.7% of registrations)
- **Largest Drop in Registrations:** Bajaj (-18.4% YoY)
- **Most Consistent Growth:** Hero (14 positive quarters)

---

## Requirements
See [`requirements.txt`](requirements.txt) for dependencies:
```
streamlit
pandas
plotly
reportlab
```

---

## Contributing
Pull requests are welcome.  
For major changes, please open an issue first to discuss what you would like to change.

---

## Contact
**Author:** Rayyan Hanchanal
**GitHub:** [rayyan-14](https://github.com/rayyan-14)  

---

## Screenshots

### Dashboard View
![Dashboard Screenshot](screenshots/dashboard.png)

### Market Share Chart
![Market Share](screenshots/pie_chart.png)
