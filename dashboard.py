import pandas as pd
import plotly.express as px
import streamlit as st
from statistics import mode, StatisticsError
import pathlib

st.set_page_config(page_title="📦 Shipment Dashboard", layout="wide")
DATA_PATH = pathlib.Path("output/flattened_shipments.csv")

@st.cache
def load_data(path):
    if not path.exists():
        st.error(f"❌ {path} not found. Run the flatten step first.")
        st.stop()
    return pd.read_csv(path)

df = load_data(DATA_PATH)
st.title("📦 Shipment Analytics Dashboard")

states = sorted(df["Drop State"].unique())
selected_states = st.multiselect("Filter by Drop State", states, default=states)
filtered = df[df["Drop State"].isin(selected_states)]

def safe_mode(series):
    try: return mode(series)
    except StatisticsError: return series.mode().iloc[0]

st.subheader("📊 Key Metrics")
k1, k2, k3 = st.columns(3)
k1.metric("Avg Days", f"{filtered['Days taken for delivery'].mean():.2f}")
k2.metric("Avg Attempts", f"{filtered['Number of delivery attempts'].mean():.2f}")
k3.metric("Common Attempts", f"{safe_mode(filtered['Number of delivery attempts']):.0f}")

st.markdown("---")

attempt_counts = filtered["Number of delivery attempts"].value_counts().sort_index()
c1, c2 = st.columns(2)

c1.plotly_chart(
    px.pie(
        names=attempt_counts.index.astype(str),
        values=attempt_counts.values,
        hole=0.4,
        title="🚚 Delivery Attempts Share"
    ),
    use_container_width=True
)

c2.plotly_chart(
    px.bar(
        x=attempt_counts.index.astype(str),
        y=attempt_counts.values,
        labels={"x": "Attempts", "y": "Shipments"},
        title="📦 Count of Delivery Attempts"
    ),
    use_container_width=True
)

st.markdown("---")

state_pct = (filtered["Drop State"].value_counts(normalize=True) * 100).round(2)
s1, s2 = st.columns(2)

s1.plotly_chart(
    px.bar(
        x=state_pct.values,
        y=state_pct.index,
        orientation="h",
        labels={"x": "Percent", "y": "State"},
        text=state_pct.values,
        title="📍 % Deliveries by State"
    ),
    use_container_width=True
)

s2.plotly_chart(
    px.pie(
        names=state_pct.index,
        values=state_pct.values,
        hole=0.3,
        title="📍 State‑wise Share"
    ),
    use_container_width=True
)

st.markdown("---")

city_pct = (filtered["Drop City"].value_counts(normalize=True) * 100).round(2)
st.plotly_chart(
    px.pie(
        names=city_pct.index,
        values=city_pct.values,
        hole=0.3,
        title="🏙️ Drop City‑wise Share"
    ),
    use_container_width=True
)

st.markdown("---")

pay_counts = filtered["Payment type"].value_counts()
p1, p2 = st.columns(2)

p1.plotly_chart(
    px.bar(
        x=pay_counts.index,
        y=pay_counts.values,
        text=pay_counts.values,
        labels={"x": "Payment Type", "y": "Shipments"},
        title="💳 COD vs Prepaid (Overall)"
    ),
    use_container_width=True
)

grouped = (
    filtered.groupby(["Drop City", "Payment type"])
    .size()
    .reset_index(name="Count")
)

fig_city_pay = px.bar(
    grouped,
    x="Drop City",
    y="Count",
    color="Payment type",
    barmode="group",
    title="🏙️ COD vs Prepaid by Drop City",
    labels={"Count": "Shipments"}
)
fig_city_pay.update_layout(xaxis_tickangle=-45)

p2.plotly_chart(fig_city_pay, use_container_width=True)

st.caption("© 2025 • By Pratik with ❤️")
