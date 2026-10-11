from data_generator import generate_telemetry
from sklearn.ensemble import IsolationForest
import plotly.express as px
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="CloudMind Intelligence Center",
    page_icon="☁️",
    layout="wide",
)

st.markdown(
    """<style>.stApp { background: #0b1020; color: #e8eefc; } [data-testid="stMetric"] { background: #151e33; border: 1px solid #283752; padding: 18px; border-radius: 12px; } [data-testid="stMetricLabel"] { color: #9db0ce; }</style>""",
    unsafe_allow_html=True,
)

st.title("☁️ CloudMind")
st.caption("CLOUD RESOURCE INTELLIGENCE CENTER • PHASE 3")
st.warning("DEMO MODE: All server telemetry and AI predictions are simulated.")

# Load telemetry data
df = generate_telemetry()

# Run anomaly detection across all servers for export prep
model = IsolationForest(contamination=0.05, random_state=42)
df["anomaly_score"] = model.fit_predict(df[["cpu_percent", "ram_percent"]])
df["is_anomaly"] = df["anomaly_score"].apply(
    lambda x: "Anomaly" if x == -1 else "Normal"
)

# Sidebar controls & Power BI Export
st.sidebar.header("Navigation & Export")
server_list = df["server_id"].unique()
selected_server = st.sidebar.selectbox("Select Server VM", server_list)

st.sidebar.divider()
st.sidebar.subheader("📊 Power BI Data Export")
st.sidebar.caption(
    "Export telemetry and AI flags as CSV files for your Power BI dashboard."
)

# Convert full dataset to CSV for download
csv_data = df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    label="Download Full Telemetry (CSV)",
    data=csv_data,
    file_name="cloudmind_telemetry_export.csv",
    mime="text/csv",
)

# Filter for selected server view
server_df = df[df["server_id"] == selected_server].sort_values("timestamp")

# Top KPI Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
  st.metric(
      "Avg CPU", f"{server_df['cpu_percent'].mean():.1f}%", delta="+2.1%"
  )
with col2:
  st.metric(
      "Avg RAM", f"{server_df['ram_percent'].mean():.1f}%", delta="-0.5%"
  )
with col3:
  st.metric(
      "Network", f"{server_df['network_mbps'].mean():.1f} Mbps", delta="+12"
  )
with col4:
  st.metric("Status", server_df["status"].iloc[-1])

# Telemetry Charts
st.subheader(f"Telemetry & Trends: {selected_server}")
fig = px.line(
    server_df,
    x="timestamp",
    y=["cpu_percent", "ram_percent"],
    template="plotly_dark",
    title="CPU & RAM Utilization Over Time",
)
st.plotly_chart(fig, use_container_width=True)

# Anomaly Detection using Isolation Forest
st.subheader("AI Anomaly Detection")
anomalies = server_df[server_df["is_anomaly"] == "Anomaly"]

if not anomalies.empty:
  st.error(
      f"⚠️ {len(anomalies)} anomalous behavior spikes detected on"
      f" {selected_server}."
  )
  st.dataframe(
      anomalies[["timestamp", "cpu_percent", "ram_percent", "status"]],
      use_container_width=True,
  )
else:
  st.success(f"No operational anomalies detected for {selected_server}.")

# Optimization Recommendations
st.subheader("Resource Optimization Recommendations")
avg_cpu = server_df["cpu_percent"].mean()
if avg_cpu > 75:
  st.warning(
      "💡 **Recommendation:** Scale up instance tier or redistribute load."
      " Predicted high resource saturation."
  )
elif avg_cpu < 30:
  st.info(
      "💡 **Recommendation:** Consider rightsizing or scaling down VM to"
      " optimize cloud costs."
  )
else:
  st.success(
      "💡 **Recommendation:** Resource utilization is optimal. No action"
      " needed."
  )