import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="Route Efficiency & Geographic Analysis",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv("Nassau Candy Distributor.csv")
df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

df["Delivery Days"] = (
    df["Ship Date"] - df["Order Date"]
).dt.days
route_summary = pd.read_csv("route_level_performance.csv")

# Make sure numeric columns are numeric
for col in ["Sales", "Units", "Gross Profit", "Cost", "Delivery Days"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

for col in ["Route_Volume", "Average_Lead_Time", "Lead_Time_Variability"]:
    if col in route_summary.columns:
        route_summary[col] = pd.to_numeric(
            route_summary[col], errors="coerce"
        )

# =========================================================
# TITLE
# =========================================================

st.title("📊 Factory-to-Customer Shipping Route Efficiency Analysis for Nassau Candy Distributor")

st.write(
    "Analysis of route efficiency, shipping performance, "
    "geographic bottlenecks and ship mode performance."
)

# =========================================================
# KPI SECTION
# =========================================================

total_records = len(df)
total_orders = df["Order ID"].nunique()
total_sales = df["Sales"].sum()
total_profit = df["Gross Profit"].sum()
total_units = df["Units"].sum()

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Records", f"{total_records:,}")
c2.metric("Total Orders", f"{total_orders:,}")
c3.metric("Total Sales", f"{total_sales:,.2f}")
c4.metric("Gross Profit", f"{total_profit:,.2f}")
c5.metric("Total Units", f"{total_units:,}")

st.divider()

# =========================================================
# 1. ROUTE EFFICIENCY OVERVIEW
# =========================================================

st.header("1️⃣ Route Efficiency Overview")

# ---------------------------------------------------------
# Average Lead Time by Route
# ---------------------------------------------------------

st.subheader("Average Lead Time by Route")

lead_time_routes = route_summary.dropna(
    subset=["Route_State", "Average_Lead_Time"]
).sort_values(
    "Average_Lead_Time",
    ascending=True
)

fig1 = px.bar(
    lead_time_routes,
    x="Average_Lead_Time",
    y="Route_State",
    orientation="h",
    title="Average Lead Time by Route",
    labels={
        "Average_Lead_Time": "Average Lead Time",
        "Route_State": "Route"
    }
)

fig1.update_layout(height=700)

st.plotly_chart(fig1, use_container_width=True)

# ---------------------------------------------------------
# Route Performance Leaderboard
# ---------------------------------------------------------

st.subheader("Route Performance Leaderboard")

leaderboard = route_summary.dropna(
    subset=["Route_State", "Average_Lead_Time"]
).sort_values(
    "Average_Lead_Time",
    ascending=True
).copy()

leaderboard["Efficiency Rank"] = range(
    1,
    len(leaderboard) + 1
)

st.dataframe(
    leaderboard[
        [
            "Efficiency Rank",
            "Route_State",
            "Route_Volume",
            "Average_Lead_Time",
            "Lead_Time_Variability"
        ]
    ],
    use_container_width=True
)

# ---------------------------------------------------------
# Top 10 / Bottom 10
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("🏆 Top 10 Most Efficient Routes")

    top10 = leaderboard.head(10)

    fig2 = px.bar(
        top10.sort_values("Average_Lead_Time"),
        x="Average_Lead_Time",
        y="Route_State",
        orientation="h",
        title="Top 10 Most Efficient Routes",
        labels={
            "Average_Lead_Time": "Average Lead Time",
            "Route_State": "Route"
        }
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

with col2:

    st.subheader("⚠️ Bottom 10 Least Efficient Routes")

    bottom10 = leaderboard.tail(10).sort_values(
        "Average_Lead_Time",
        ascending=True
    )

    fig3 = px.bar(
        bottom10,
        x="Average_Lead_Time",
        y="Route_State",
        orientation="h",
        title="Bottom 10 Least Efficient Routes",
        labels={
            "Average_Lead_Time": "Average Lead Time",
            "Route_State": "Route"
        }
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# =========================================================
# 2. GEOGRAPHIC SHIPPING MAP
# =========================================================

st.header("2️⃣ Geographic Shipping Analysis")

# State-level aggregation

state_summary = df.groupby(
    "State/Province",
    dropna=True
).agg(
    Shipments=("Order ID", "count"),
    Orders=("Order ID", "nunique"),
    Sales=("Sales", "sum"),
    Average_Lead_Time=("Delivery Days", "mean"),
    Gross_Profit=("Gross Profit", "sum")
).reset_index()

# ---------------------------------------------------------
# State Performance
# ---------------------------------------------------------

st.subheader("Regional Performance")

fig4 = px.bar(
    state_summary.sort_values(
        "Average_Lead_Time",
        ascending=False
    ),
    x="State/Province",
    y="Average_Lead_Time",
    title="Average Lead Time by State / Province",
    labels={
        "State/Province": "State / Province",
        "Average_Lead_Time": "Average Lead Time"
    }
)

fig4.update_layout(
    xaxis_tickangle=-45,
    height=600
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# ---------------------------------------------------------
# Geographic Shipping Map
# ---------------------------------------------------------

st.subheader("Geographic Shipping Map")

# State name → US abbreviation
state_codes = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ",
    "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE", "Florida": "FL",
    "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

state_map = state_summary.copy()

state_map["State_Code"] = state_map[
    "State/Province"
].map(state_codes)

state_map = state_map.dropna(
    subset=["State_Code"]
)

if len(state_map) > 0:

    fig5 = px.choropleth(
        state_map,
        locations="State_Code",
        locationmode="USA-states",
        color="Average_Lead_Time",
        scope="usa",
        hover_name="State/Province",
        hover_data=[
            "Shipments",
            "Orders",
            "Sales",
            "Average_Lead_Time"
        ],
        title="Geographic Shipping Performance"
    )

    fig5.update_layout(height=650)

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

else:

    st.info(
        "State names could not be matched to the geographic map. "
        "The regional performance chart above is available instead."
    )

# ---------------------------------------------------------
# Regional Bottlenecks
# ---------------------------------------------------------

st.subheader("🚧 Regional Bottleneck Visualization")

bottlenecks = state_summary.sort_values(
    "Average_Lead_Time",
    ascending=False
).head(10)

fig6 = px.bar(
    bottlenecks,
    x="Average_Lead_Time",
    y="State/Province",
    orientation="h",
    title="Top Regional Bottlenecks",
    labels={
        "Average_Lead_Time": "Average Lead Time",
        "State/Province": "Region"
    }
)

fig6.update_layout(height=600)

st.plotly_chart(
    fig6,
    use_container_width=True
)

# =========================================================
# 3. SHIP MODE COMPARISON
# =========================================================

st.header("3️⃣ Ship Mode Comparison")

ship_mode_summary = df.groupby(
    "Ship Mode",
    dropna=True
).agg(
    Shipments=("Order ID", "count"),
    Orders=("Order ID", "nunique"),
    Average_Lead_Time=("Delivery Days", "mean"),
    Sales=("Sales", "sum"),
    Gross_Profit=("Gross Profit", "sum")
).reset_index()

st.subheader("Lead Time Comparison by Shipping Method")

fig7 = px.bar(
    ship_mode_summary.sort_values(
        "Average_Lead_Time"
    ),
    x="Ship Mode",
    y="Average_Lead_Time",
    title="Average Lead Time by Shipping Method",
    labels={
        "Ship Mode": "Shipping Method",
        "Average_Lead_Time": "Average Lead Time"
    }
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

st.dataframe(
    ship_mode_summary,
    use_container_width=True
)

# =========================================================
# 4. ROUTE DRILL-DOWN
# =========================================================

st.header("4️⃣ Route Drill-Down")

selected_state = st.selectbox(
    "Select a State / Province",
    sorted(
        df["State/Province"]
        .dropna()
        .unique()
        .tolist()
    )
)

state_data = df[
    df["State/Province"] == selected_state
]

# ---------------------------------------------------------
# State-level insights
# ---------------------------------------------------------

st.subheader(
    f"State-Level Performance: {selected_state}"
)

s1, s2, s3, s4 = st.columns(4)

s1.metric(
    "Shipments",
    f"{len(state_data):,}"
)

s2.metric(
    "Orders",
    f"{state_data['Order ID'].nunique():,}"
)

s3.metric(
    "Sales",
    f"{state_data['Sales'].sum():,.2f}"
)

s4.metric(
    "Avg Lead Time",
    f"{state_data['Delivery Days'].mean():.2f}"
)

# ---------------------------------------------------------
# City-level shipment insights
# ---------------------------------------------------------

st.subheader(
    f"City-Level Shipment Insights: {selected_state}"
)

city_summary = state_data.groupby(
    "City",
    dropna=True
).agg(
    Shipments=("Order ID", "count"),
    Orders=("Order ID", "nunique"),
    Sales=("Sales", "sum"),
    Average_Lead_Time=("Delivery Days", "mean"),
    Gross_Profit=("Gross Profit", "sum")
).reset_index()

city_summary = city_summary.sort_values(
    "Shipments",
    ascending=False
)

st.dataframe(
    city_summary,
    use_container_width=True
)

fig8 = px.bar(
    city_summary.head(10),
    x="Shipments",
    y="City",
    orientation="h",
    title=f"Top 10 Cities by Shipments - {selected_state}",
    labels={
        "Shipments": "Shipments",
        "City": "City"
    }
)

fig8.update_layout(height=500)

st.plotly_chart(
    fig8,
    use_container_width=True
)

# =========================================================
# FINAL MESSAGE
# =========================================================

st.success(
    "Dashboard analysis completed successfully."
)