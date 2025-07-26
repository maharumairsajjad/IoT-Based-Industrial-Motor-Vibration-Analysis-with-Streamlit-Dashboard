# This is streamlit Dashboard code

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os

# Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate(r"C:\Users\Abdullah\Downloads\hello\test2-f1565-firebase-adminsdk-bh9a8-c07705abb7.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": " " # add your own databaseurl 
    })

# Function to fetch data from Firebase Realtime Database
def fetch_realtime_db_data():
    try:
        ref = db.reference("sensor_data")  # Reference to the 'sensor_data' node
        return ref.get() or {}
    except Exception as e:
        st.error(f"Failed to fetch data from Realtime Database: {e}")
        return {}

# Initialize session state for data storage
if "sensor_data" not in st.session_state:
    st.session_state.sensor_data = {
        "time": [],
        "acc_x": [],
        "acc_y": [],
        "acc_z": [],
        "gyro_x": [],
        "gyro_y": [],
        "gyro_z": [],
        "temp": []
    }

# Streamlit Dashboard Layout
st.set_page_config(page_title="MPU6050 Sensor Dashboard", layout="wide")
st.title("📊 MPU6050 Vibration and Temperature Analysis Dashboard")
st.write("Real-time data fetched from Firebase.")

# Sidebar Configuration
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", min_value=1, max_value=10, value=5)
st.sidebar.subheader("Alert Thresholds")
acc_threshold = st.sidebar.number_input("Acceleration Threshold (m/s²)", min_value=0.0, value=10.0)
gyro_threshold = st.sidebar.number_input("Gyroscope Threshold (°/s)", min_value=0.0, value=100.0)
temp_threshold = st.sidebar.number_input("Temperature Threshold (°C)", min_value=0.0, value=50.0)

# Trigger auto-refresh
st_autorefresh(interval=refresh_rate * 1000, key="autorefresh")

# Fetch data from Firebase
sensor_data = fetch_realtime_db_data()

if sensor_data:
    # Parse data
    acceleration = sensor_data.get("acceleration", {})
    gyroscope = sensor_data.get("gyroscope", {})
    temperature = sensor_data.get("temperature", 0)

    # Add data to session state
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.sensor_data["time"].append(now)
    st.session_state.sensor_data["acc_x"].append(acceleration.get("x", 0))
    st.session_state.sensor_data["acc_y"].append(acceleration.get("y", 0))
    st.session_state.sensor_data["acc_z"].append(acceleration.get("z", 0))
    st.session_state.sensor_data["gyro_x"].append(gyroscope.get("x", 0))
    st.session_state.sensor_data["gyro_y"].append(gyroscope.get("y", 0))
    st.session_state.sensor_data["gyro_z"].append(gyroscope.get("z", 0))
    st.session_state.sensor_data["temp"].append(temperature)

    # Convert data to Pandas DataFrame
    df = pd.DataFrame({
        "Time": st.session_state.sensor_data["time"],
        "Acc_X": st.session_state.sensor_data["acc_x"],
        "Acc_Y": st.session_state.sensor_data["acc_y"],
        "Acc_Z": st.session_state.sensor_data["acc_z"],
        "Gyro_X": st.session_state.sensor_data["gyro_x"],
        "Gyro_Y": st.session_state.sensor_data["gyro_y"],
        "Gyro_Z": st.session_state.sensor_data["gyro_z"],
        "Temperature": st.session_state.sensor_data["temp"]
    })

    # Log data to CSV
    csv_file = "sensor_data_log.csv"
    if not os.path.exists(csv_file):
        df.to_csv(csv_file, index=False)
    else:
        df.to_csv(csv_file, mode="a", header=False, index=False)

    # Alerts for thresholds
    st.subheader("Alerts")
    alerts = []
    if any(abs(val) > acc_threshold for val in df[["Acc_X", "Acc_Y", "Acc_Z"]].iloc[-1]):
        alerts.append("Acceleration exceeded threshold!")
    if any(abs(val) > gyro_threshold for val in df[["Gyro_X", "Gyro_Y", "Gyro_Z"]].iloc[-1]):
        alerts.append("Gyroscope exceeded threshold!")
    if df["Temperature"].iloc[-1] > temp_threshold:
        alerts.append("Temperature exceeded threshold!")

    if alerts:
        for alert in alerts:
            st.error(alert)
    else:
        st.success("All readings are within thresholds.")

    # Plotly Graphs
    st.subheader("Acceleration (m/s²)")
    fig_acc = go.Figure()
    fig_acc.add_trace(go.Scatter(x=df["Time"], y=df["Acc_X"], mode="lines", name="Acc_X"))
    fig_acc.add_trace(go.Scatter(x=df["Time"], y=df["Acc_Y"], mode="lines", name="Acc_Y"))
    fig_acc.add_trace(go.Scatter(x=df["Time"], y=df["Acc_Z"], mode="lines", name="Acc_Z"))
    fig_acc.update_layout(xaxis_title="Time", yaxis_title="Acceleration (m/s²)")
    st.plotly_chart(fig_acc, use_container_width=True)

    st.subheader("Gyroscope (°/s)")
    fig_gyro = go.Figure()
    fig_gyro.add_trace(go.Scatter(x=df["Time"], y=df["Gyro_X"], mode="lines", name="Gyro_X"))
    fig_gyro.add_trace(go.Scatter(x=df["Time"], y=df["Gyro_Y"], mode="lines", name="Gyro_Y"))
    fig_gyro.add_trace(go.Scatter(x=df["Time"], y=df["Gyro_Z"], mode="lines", name="Gyro_Z"))
    fig_gyro.update_layout(xaxis_title="Time", yaxis_title="Gyroscope (°/s)")
    st.plotly_chart(fig_gyro, use_container_width=True)

    st.subheader("Temperature (°C)")
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=df["Time"], y=df["Temperature"], mode="lines", name="Temperature"))
    fig_temp.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

    # Historical Data Analysis
    st.sidebar.subheader("Upload Historical Data")
    uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])
    if uploaded_file:
        historical_df = pd.read_csv(uploaded_file)
        st.subheader("Historical Data")
        st.write(historical_df)
        st.line_chart(historical_df)

else:
    st.warning("No data available from Firebase.")
