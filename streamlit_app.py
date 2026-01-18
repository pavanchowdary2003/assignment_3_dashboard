import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")



# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["hour"] = df["datetime"].dt.hour


    def get_day_period(hour):
            if hour < 6:
                return "Night"
            elif hour < 12:
                return "Morning"
            elif hour < 18:
                return "Afternoon"
            else:
                return "Evening"

    df["day_period"] = df["hour"].apply(get_day_period)

    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    df["season"] = df["season"].map(season_map)

    return df

df = load_data()

# Sidebar widgets
st.sidebar.header("Filters")

year_selected = st.sidebar.multiselect(
    "Select Year",
    options=df["year"].unique(),
    default=df["year"].unique()
)

season_selected = st.sidebar.multiselect(
    "Select Season",
    options=df["season"].unique(),
    default=df["season"].unique()
)

working_day = st.sidebar.radio(
    "Working Day",
    ["All", "Working Day", "Non-Working Day"]
)

# Apply filters
filtered_df = df[
    (df["year"].isin(year_selected)) &
    (df["season"].isin(season_selected))
]

if working_day == "Working Day":
    filtered_df = filtered_df[filtered_df["workingday"] == 1]
elif working_day == "Non-Working Day":
    filtered_df = filtered_df[filtered_df["workingday"] == 0]

# Title
st.title("🚲 Bike Sharing Demand Dashboard")
st.markdown("Interactive analysis of Washington D.C. bike rentals (2011–2012)")

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Total Rentals", int(filtered_df["count"].sum()))
col2.metric("Average Hourly Rentals", round(filtered_df["count"].mean(), 2))
col3.metric("Peak Hour Rentals", int(filtered_df["count"].max()))

# -----------------------------
# Plot 1: Mean Rentals by Hour
# -----------------------------
st.subheader("Mean Hourly Bike Rentals by Hour of Day")

hourly_mean = filtered_df.groupby("hour")["count"].mean()

fig, ax = plt.subplots()
ax.plot(hourly_mean.index, hourly_mean.values)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Mean Rentals")
ax.set_xticks(range(0, 24))

st.pyplot(fig)

# ---------------------------------------
# Plot 2: Mean Rentals by Month
# ---------------------------------------
st.subheader("Mean Bike Rentals by Month")

monthly_mean = (
    filtered_df
    .groupby("month")["count"]
    .mean()
)

fig, ax = plt.subplots()
ax.plot(monthly_mean.index, monthly_mean.values, marker='o')
ax.set_xlabel("Month")
ax.set_ylabel("Mean Rentals")
ax.set_title("Monthly Bike Rental Demand")

st.pyplot(fig)

# ---------------------------------------
# ---------------------------------------
# Plot 3: Working Day vs Non-Working Day
# ---------------------------------------
st.subheader("Mean Hourly Rentals: Working vs Non-Working Days")

workingday_mean = (
    filtered_df
    .groupby("workingday")["count"]
    .mean()
    .rename({0: "Non-Working Day", 1: "Working Day"})
)

fig, ax = plt.subplots()
ax.bar(workingday_mean.index.astype(str), workingday_mean.values)
ax.set_xlabel("Day Type")
ax.set_ylabel("Mean Rentals")

st.pyplot(fig)



# ---------------------------------------
# Plot 4: Weather vs Rentals (Mean + 95% CI)
# ---------------------------------------
st.subheader("Mean Hourly Rentals by Weather Category (95% CI)")

weather_stats = (
    filtered_df
    .groupby("weather")["count"]
    .agg(["mean", "std", "count"])
)

weather_stats["ci"] = 1.96 * weather_stats["std"] / (weather_stats["count"] ** 0.5)

fig, ax = plt.subplots()
ax.bar(
    weather_stats.index.astype(str),
    weather_stats["mean"],
    yerr=weather_stats["ci"],
    capsize=5
)

ax.set_xlabel("Weather Category")
ax.set_ylabel("Mean Rentals")

st.pyplot(fig)


# ---------------------------------------
# Plot 5: Rentals by Day Period
# ---------------------------------------
st.subheader("Mean Hourly Rentals by Period of the Day")

day_period_mean = (
    filtered_df
    .groupby("day_period")["count"]
    .mean()
    .reindex(["Night", "Morning", "Afternoon", "Evening"])
)

fig, ax = plt.subplots()
ax.bar(day_period_mean.index, day_period_mean.values)
ax.set_xlabel("Day Period")
ax.set_ylabel("Mean Rentals")

st.pyplot(fig)



st.markdown("""
*Key Insights:*
- Bike rentals peak during morning and evening commute hours.
- Summer months show the highest average demand.
- Working days have higher rentals compared to non-working days.
- Clear weather conditions significantly increase bike usage.
""")
