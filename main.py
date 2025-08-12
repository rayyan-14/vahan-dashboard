import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_utils import calculate_growth
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import base64
import tempfile

# ------------------ PDF GENERATOR (CHARTS ONLY) ------------------
def generate_pdf(kpis,insights, *chart_paths):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Vehicle Registration Dashboard Report")

    # Date
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # KPIs
    c.setFont("Helvetica-Bold", 12)
    y = height - 110
    for title, value in kpis.items():
        c.drawString(50, y, f"{title}: {value}")
        y -= 20

    # Insights Section
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Insights:")
    y -= 20
    c.setFont("Helvetica", 10)
    for insight in insights_list:
        c.drawString(60, y, f"- {insight}")
        y -= 15
        if y < 100:  # Avoid page break in middle
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

    # Charts
    y -= 30
    for chart_path in chart_paths:
        if y < 250:
            c.showPage()
            y = height - 50
        c.drawImage(chart_path, 50, y - 200, width=500, height=200, preserveAspectRatio=True)
        y -= 220

    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ------------------ PDF GENERATOR (TABLE ONLY) ------------------
def generate_table_pdf(filtered_df):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Full Vehicle Registration Data")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Table Header
    y = height - 100
    c.setFont("Helvetica-Bold", 9)
    headers = ["Month", "Category", "Manufacturer", "State", "FuelType", "Registrations", "QoQ_Growth", "YoY_Growth"]
    x_positions = [50, 120, 220, 350, 430, 500, 560, 620]

    for x, h in zip(x_positions, headers):
        c.drawString(x, y, h)

    y -= 15
    c.line(50, y, width - 50, y)

    # Table Rows
    c.setFont("Helvetica", 8)
    for _, row in filtered_df.iterrows():
        y -= 12
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica-Bold", 9)
            for x, h in zip(x_positions, headers):
                c.drawString(x, y, h)
            y -= 15
            c.setFont("Helvetica", 8)

        values = [
            str(row["Month"]),
            str(row["Category"]),
            str(row["Manufacturer"]),
            str(row.get("State", "")),
            str(row.get("FuelType", "")),
            str(row["Registrations"]),
            str(round(row["QoQ_Growth"], 2)),
            str(round(row["YoY_Growth"], 2))
        ]
        for x, v in zip(x_positions, values):
            c.drawString(x, y, v)

    c.save()
    buffer.seek(0)
    return buffer

# ------------------ TEMP SAVE HELPER ------------------
def save_chart_temp(fig):
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.write_image(tmp_file.name, format="png")
    return tmp_file.name

# ------------------ STREAMLIT APP ------------------
st.set_page_config(page_title="Vehicle Registration Dashboard", layout="wide")
st.title("📊 Vehicle Registration Dashboard (Demo)")

# Load Data
df = pd.read_csv("vehicle_data_big.csv")
df = calculate_growth(df)

# Sidebar Filters
st.sidebar.header("Filters")
categories = st.sidebar.multiselect("Select Vehicle Types", options=df["Category"].unique(), default=df["Category"].unique())
manufacturers = st.sidebar.multiselect("Select Manufacturers", options=df["Manufacturer"].unique(), default=df["Manufacturer"].unique())

states = []
if "State" in df.columns:
    states = st.sidebar.multiselect("Select States", options=df["State"].unique(), default=df["State"].unique())

fueltypes = []
if "FuelType" in df.columns:
    fueltypes = st.sidebar.multiselect("Select Fuel Types", options=df["FuelType"].unique(), default=df["FuelType"].unique())

date_range = st.sidebar.slider("Select Year Range", min_value=int(df["Year"].min()), max_value=int(df["Year"].max()), value=(int(df["Year"].min()), int(df["Year"].max())), step=1)

# Apply Filters
filtered = df[
    df["Category"].isin(categories) &
    df["Manufacturer"].isin(manufacturers) &
    df["Year"].between(date_range[0], date_range[1])
]
if states:
    filtered = filtered[filtered["State"].isin(states)]
if fueltypes:
    filtered = filtered[filtered["FuelType"].isin(fueltypes)]

if filtered.empty:
    st.warning("No data matches the filters. Please change filters.")
    st.stop()

# --- CHARTS ---
# 1. Registration Trend
fig_reg = px.line(filtered, x="Month", y="Registrations", color="Manufacturer", markers=True, title="Vehicle Registration Trend")
fig_reg.update_layout(xaxis_title="Month", yaxis_title="Registrations", xaxis=dict(tickangle=-45))

# 2. Growth Trends
fig_growth = go.Figure()
for m in filtered["Manufacturer"].unique():
    sub = filtered[filtered["Manufacturer"] == m]
    fig_growth.add_trace(go.Scatter(x=sub["Month"], y=sub["QoQ_Growth"], mode='lines+markers', name=f"{m} QoQ"))
    fig_growth.add_trace(go.Scatter(x=sub["Month"], y=sub["YoY_Growth"], mode='lines+markers', name=f"{m} YoY", line=dict(dash='dash')))
fig_growth.update_layout(title="Quarter-over-Quarter & Year-over-Year Growth", xaxis_title="Month", yaxis_title="Growth %", xaxis=dict(tickangle=-45))
st.plotly_chart(fig_growth, use_container_width=True)
# 3. Market Share Pie
market_share = filtered.groupby("Manufacturer")["Registrations"].sum().reset_index()
fig_pie = px.pie(
    market_share,
    values="Registrations",
    names="Manufacturer",
    title="Market Share (Filtered Selection)",
    hole=0.4
)
st.plotly_chart(fig_pie, use_container_width=True, key="market_share_pie")

 #4. EV vs Non-EV Trend
fig_ev_trend = None
if "FuelType" in filtered.columns:
    ev_data = filtered.groupby(["Month", "FuelType"])["Registrations"].sum().reset_index()
    if not ev_data.empty:
        fig_ev_trend = px.line(ev_data, x="Month", y="Registrations", color="FuelType", markers=True, title="EV vs Non-EV Registration Trend")
        fig_ev_trend.update_layout(xaxis_title="Month", yaxis_title="Registrations", xaxis=dict(tickangle=-45))
        st.plotly_chart(fig_ev_trend, use_container_width=True)

# 5. EV Adoption %
fig_ev_adoption = None
if "FuelType" in filtered.columns:
    ev_data = filtered.groupby(["Month", "FuelType"])["Registrations"].sum().reset_index()
    total_per_month = ev_data.groupby("Month")["Registrations"].sum().reset_index(name="Total")
    ev_only = ev_data[ev_data["FuelType"].str.lower() == "electric"].merge(total_per_month, on="Month")
    ev_only["EV_Percent"] = (ev_only["Registrations"] / ev_only["Total"]) * 100
    if not ev_only.empty:
        fig_ev_adoption = px.line(ev_only, x="Month", y="EV_Percent", markers=True, title="EV Adoption Trend (%)")
        fig_ev_adoption.update_layout(yaxis_title="EV % of Total Registrations", xaxis_title="Month", xaxis=dict(tickangle=-45))
        st.plotly_chart(fig_ev_adoption, use_container_width=True)

# --- KPI CALCS ---
total_registrations = int(filtered["Registrations"].sum())
top_manufacturer = filtered.groupby("Manufacturer")["Registrations"].sum().idxmax()
top_manufacturer_value = int(filtered.groupby("Manufacturer")["Registrations"].sum().max())
best_qoq_row = filtered.loc[filtered["QoQ_Growth"].idxmax()]
best_qoq_label = f"{best_qoq_row['Manufacturer']} ({best_qoq_row['Month']})"
best_qoq_value = round(best_qoq_row["QoQ_Growth"], 2)
worst_qoq_row = filtered.loc[filtered["QoQ_Growth"].idxmin()]
worst_qoq_label = f"{worst_qoq_row['Manufacturer']} ({worst_qoq_row['Month']})"
worst_qoq_value = round(worst_qoq_row["QoQ_Growth"], 2)

kpi_dict = {
    "Total Registrations": f"{total_registrations:,}",
    "Top Manufacturer": f"{top_manufacturer} ({top_manufacturer_value:,})",
    "Best QoQ Growth": f"{best_qoq_label} ({best_qoq_value}%)",
    "Worst QoQ Growth": f"{worst_qoq_label} ({worst_qoq_value}%)"
}

# KPI Display
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Registrations", f"{total_registrations:,}")
col2.metric("Top Manufacturer", top_manufacturer, f"{top_manufacturer_value:,}")
col3.metric("Best QoQ Growth", best_qoq_label, f"{best_qoq_value}%")
col4.metric("Worst QoQ Growth", worst_qoq_label, f"{worst_qoq_value}%")

# Data Table
st.subheader("Filtered Data with Growth %")
st.dataframe(filtered[["Month", "Category", "Manufacturer", "Registrations", "QoQ_Growth", "YoY_Growth"]])

# Insights function
def generate_insights(filtered_df):
    insights_list = []

    # 1️⃣ Highest EV Adoption State
    if "FuelType" in filtered_df.columns and "State" in filtered_df.columns:
        ev_by_state = (
            filtered_df.groupby("State").apply(
                lambda x: (x[x["FuelType"].str.lower() == "electric"]["Registrations"].sum() /
                           x["Registrations"].sum()) * 100
            ).reset_index(name="EV_Percent")
        )
        if not ev_by_state.empty:
            top_ev_state = ev_by_state.loc[ev_by_state["EV_Percent"].idxmax()]
            insights_list.append(f"Highest EV Adoption State: **{top_ev_state['State']} ({top_ev_state['EV_Percent']:.1f}%)**")

    # 2️⃣ Fastest Growing Manufacturer YoY
    if "YoY_Growth" in filtered_df.columns:
        yoy_growth = (
            filtered_df.groupby("Manufacturer")["YoY_Growth"].mean().reset_index()
        )
        if not yoy_growth.empty:
            top_growth = yoy_growth.loc[yoy_growth["YoY_Growth"].idxmax()]
            insights_list.append(f"Fastest Growing Manufacturer YoY: **{top_growth['Manufacturer']} (+{top_growth['YoY_Growth']:.1f}%)**")

            # 4️⃣ Largest Drop in Registrations (YoY)
            yoy_drop = yoy_growth.loc[yoy_growth["YoY_Growth"].idxmin()]
            insights_list.append(f"Largest Drop in Registrations: **{yoy_drop['Manufacturer']} ({yoy_drop['YoY_Growth']:.1f}% YoY)**")

    # 3️⃣ Most Popular Fuel Type
    if "FuelType" in filtered_df.columns:
        fuel_popularity = (
            filtered_df.groupby("FuelType")["Registrations"].sum().reset_index()
        )
        if not fuel_popularity.empty:
            top_fuel = fuel_popularity.loc[fuel_popularity["Registrations"].idxmax()]
            total_regs = fuel_popularity["Registrations"].sum()
            percent = (top_fuel["Registrations"] / total_regs) * 100
            insights_list.append(f"Most Popular Fuel Type: **{top_fuel['FuelType']} ({percent:.1f}% of registrations)**")

    # 5️⃣ Most Consistent Growth
    if "QoQ_Growth" in filtered_df.columns:
        consistency = (
            filtered_df.groupby("Manufacturer")["QoQ_Growth"].apply(lambda x: (x > 0).sum()).reset_index(name="Positive_Quarters")
        )
        if not consistency.empty:
            top_consistent = consistency.loc[consistency["Positive_Quarters"].idxmax()]
            insights_list.append(f"Most Consistent Growth: **{top_consistent['Manufacturer']} ({top_consistent['Positive_Quarters']} positive quarters)**")

    return insights_list  # ✅ Return the list


# Generate Insights
insights_list = generate_insights(filtered)

# Display Insights in Streamlit
st.subheader("🔍 Additional Insights")
if insights_list:
    for insight in insights_list:
        st.markdown(f"- {insight}")
else:
    st.write("No additional insights available for current filters.")

# Save Charts for PDF
pie_chart_path = save_chart_temp(fig_pie)
ev_chart_path = save_chart_temp(fig_ev_trend)
ev_trend_path=save_chart_temp(fig_ev_adoption)
growth_trend_path=save_chart_temp(fig_growth)

# Main Report PDF
pdf_buffer=generate_pdf(kpi_dict, insights_list,growth_trend_path,pie_chart_path, ev_chart_path, ev_trend_path)
b64 = base64.b64encode(pdf_buffer.read()).decode()
st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="dashboard_report.pdf">📄 Download Report with Insights and Charts (PDF)</a>', unsafe_allow_html=True)

# Table PDF
table_pdf_buffer = generate_table_pdf(filtered)
b64_table = base64.b64encode(table_pdf_buffer.read()).decode()
st.markdown(f'<a href="data:application/pdf;base64,{b64_table}" download="full_data_table.pdf">📄 Download Full Dataset (PDF)</a>', unsafe_allow_html=True)
