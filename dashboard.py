import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

DB_URL = "postgresql://user:password@localhost:5432/crypto_db"

st.set_page_config(page_title="BTC 5s Line", layout="wide")
st.title("⚡ BTCUSDT Live Line (5s buckets)")

# Auto-rerun (no infinite loops)
st_autorefresh(interval=1000, key="refresh_1s")

@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

engine = get_engine()

# Controls
colA, colB = st.columns(2)
with colA:
    lookback_minutes = st.slider("Lookback (minutes)", 1, 120, 10)
with colB:
    bucket_seconds = st.selectbox("Bucket size (seconds)", [5, 10, 15, 30], index=0)

# Fetch recent ticks (Postgres)
# Assumes trades table: symbol, price, quantity, timestamp (ms)
query = f"""
SELECT symbol, price, quantity, timestamp
FROM trades
WHERE symbol = 'BTCUSDT'
  AND to_timestamp(timestamp/1000.0) >= now() - interval '{lookback_minutes} minutes'
ORDER BY timestamp ASC
"""
df = pd.read_sql(query, engine)

if df.empty:
    st.warning("No tick data yet. Waiting for Kafka/Spark writes...")
    st.stop()

# Convert timestamp(ms) -> datetime
df["dt"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert("Asia/Kolkata")

# ---- 5-second bucketing in pandas ----
df = df.set_index("dt")

bucket = f"{bucket_seconds}S"
agg = (
    df["price"]
    .resample(bucket)
    .mean()
    .dropna()
    .to_frame(name="avg_price")
)

# Optional: volume per bucket (sum quantity)
vol = df["quantity"].resample(bucket).sum().to_frame(name="volume")
agg = agg.join(vol, how="left").fillna(0)

latest_price = float(df["price"].iloc[-1])
avg_lookback = float(df["price"].mean())
latest_bucket_price = float(agg["avg_price"].iloc[-1])
latest_bucket_volume = float(agg["volume"].iloc[-1])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Latest Tick Price", f"${latest_price:,.2f}")
k2.metric(f"Latest {bucket_seconds}s Avg", f"${latest_bucket_price:,.2f}")
k3.metric(f"Avg Price ({lookback_minutes}m)", f"${avg_lookback:,.2f}")
k4.metric(f"Latest {bucket_seconds}s Volume", f"{latest_bucket_volume:.6f}")

# ---- Plotly line chart (zoom persists) ----
fig = go.Figure(
    data=[
        go.Scatter(
            x=agg.index,
            y=agg["avg_price"],
            mode="lines",
            name=f"Avg Price ({bucket_seconds}s)"
        )
    ]
)

fig.update_layout(
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis_title="Time (IST)",
    yaxis_title="Price",
    uirevision=f"btc_line_{bucket_seconds}_{lookback_minutes}",  # preserves zoom unless you change settings
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"scrollZoom": True, "displaylogo": False, "responsive": True},
)
