import streamlit as st
import pandas as pd
import joblib
import datetime
import requests

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Sales Forecaster",
    layout="wide"
)

# ---------------- LOAD ARTIFACTS ----------------
@st.cache_resource
def load_artifacts():
    model = joblib.load("artifacts/xgboost_model.pkl")
    item_stats = pd.read_csv("artifacts/item_stats.csv")
    return model, item_stats

model, item_stats = load_artifacts()

# ---------------- USD → INR ----------------
@st.cache_data(ttl=3600)
def get_usd_to_inr():
    try:
        url = "https://api.exchangerate.host/latest"
        params = {"base": "USD", "symbols": "INR"}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        return data["rates"]["INR"]
    except Exception:
        return None

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔮 Scenario Planner")

forecast_date = st.sidebar.date_input(
    "Forecast Date (2016 - 2036)",
    datetime.date.today() + datetime.timedelta(days=1)
)

store_ids = sorted(item_stats["Store_ID"].unique())
store_id = st.sidebar.selectbox("Select Store ID (1- 45)", store_ids)

item_ids = sorted(
    item_stats[item_stats["Store_ID"] == store_id]["Item_ID"].unique()
)
item_id = st.sidebar.selectbox("Select Item ID (1 - 99)", item_ids)

st.sidebar.markdown("---")
marketing_boost = st.sidebar.slider(
    "Marketing Boost Multiplier",
    0.8, 1.5, 1.0
)

# ---------------- FEATURE CREATION ----------------
def create_features(date, store_id, item_id, stats_df, boost):
    day_of_week = date.weekday()
    month = date.month
    is_weekend = int(day_of_week >= 5)

    row = stats_df[
        (stats_df["Store_ID"] == store_id) &
        (stats_df["Item_ID"] == item_id)
    ].iloc[0]

    rolling_avg_30 = row["Sales_Rolling_30"] * boost
    sales_proxy = rolling_avg_30  # fallback proxy when lag unavailable

    input_df = pd.DataFrame({
        "Sales_Lag_7": [sales_proxy],
        "Sales_Rolling_30": [rolling_avg_30],
        "DayOfWeek": [day_of_week],
        "Month": [month],
        "IsWeekend": [is_weekend]
    })

    return input_df

# ---------------- MAIN UI ----------------
st.title("📈 Robust Sales Forecasting System")
st.markdown("""
This model **avoids data leakage** by using only past information  
(lagged sales, rolling averages, and calendar features).
""")

input_df = create_features(
    forecast_date,
    store_id,
    item_id,
    item_stats,
    marketing_boost
)

st.subheader("Model Input Features")
st.dataframe(input_df)

if st.button("Generate Forecast"):
    prediction = model.predict(input_df)[0]
    usd_to_inr = get_usd_to_inr()

    if usd_to_inr:
        inr_value = prediction * usd_to_inr
        st.metric(
            label=f"Predicted Sales (Store {store_id}, Item {item_id})",
            value=f"₹{inr_value:,.2f}",
            delta=f"USD→INR @ {usd_to_inr:.2f}"
        )
    else:
        st.metric(
            label=f"Predicted Sales (Store {store_id}, Item {item_id})",
            value=f"${prediction:,.2f}",
            delta="Exchange rate unavailable"
        )

    if prediction < 0:
        st.error("⚠️ Model predicted negative sales. Check assumptions.")
    else:
        st.success("Forecast generated using leakage-safe features.")
