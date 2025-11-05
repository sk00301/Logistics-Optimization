import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Page configuration
st.set_page_config(
    page_title="IntelliLoad Analytics",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Force metric visibility */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #262730 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #31333F !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
    }
    /* Ensure containers are visible */
    .stColumn {
        background-color: transparent !important;
    }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():
    """Load all necessary datasets"""
    try:
        # Try to load optimized assignment first
        if os.path.exists("optimized_assignment.csv"):
            optimized_df = pd.read_csv("optimized_assignment.csv")
        else:
            st.error("⚠️ optimized_assignment.csv not found. Please run the optimization first.")
            return None, None, None, None, None, None, None
        
        # Load other datasets
        data_files = {
            'orders': 'data/orders.csv',
            'delivery': 'data/delivery_performance.csv',
            'routes': 'data/routes_distance.csv',
            'fleet': 'data/vehicle_fleet.csv',
            'warehouses': 'data/warehouse_inventory.csv',
            'feedback': 'data/customer_feedback.csv',
            'costs': 'data/cost_breakdown.csv'
        }
        
        datasets = {}
        for name, path in data_files.items():
            if os.path.exists(path):
                datasets[name] = pd.read_csv(path)
            else:
                st.warning(f"⚠️ {path} not found")
                datasets[name] = pd.DataFrame()
        
        return (optimized_df, datasets['orders'], datasets['delivery'], 
                datasets['routes'], datasets['fleet'], datasets['warehouses'], 
                datasets['feedback'])
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None, None

# ============================================================
# MAIN APP
# ============================================================

def main():
    # Header
    st.markdown('<p class="main-header">🚚 IntelliLoad Analytics Dashboard</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    optimized_df, orders_df, delivery_df, routes_df, fleet_df, warehouses_df, feedback_df = load_data()
    
    if optimized_df is None:
        st.stop()
    
    # Quick data validation
    st.sidebar.success(f"✅ Data loaded: {len(optimized_df)} orders")
    st.sidebar.info(f"📊 Columns: {len(optimized_df.columns)}")
    
    # Show a sample if debug mode is on
    if st.sidebar.checkbox("Show Raw Data Sample", value=False):
        st.sidebar.dataframe(optimized_df.head(2))
    
    # Sidebar filters
    st.sidebar.header("📊 Filters & Controls")
    
    # Date range filter (if available)
    if 'order_date' in optimized_df.columns:
        optimized_df['order_date'] = pd.to_datetime(optimized_df['order_date'], errors='coerce')
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(optimized_df['order_date'].min(), optimized_df['order_date'].max()),
            key='date_range'
        )
    
    # Vehicle type filter
    if 'vehicle_type' in optimized_df.columns:
        vehicle_types = ['All'] + list(optimized_df['vehicle_type'].dropna().unique())
        selected_vehicle = st.sidebar.selectbox("Vehicle Type", vehicle_types)
        if selected_vehicle != 'All':
            optimized_df = optimized_df[optimized_df['vehicle_type'] == selected_vehicle]
    
    # Customer segment filter
    if 'customer_segment' in optimized_df.columns:
        segments = ['All'] + list(optimized_df['customer_segment'].dropna().unique())
        selected_segment = st.sidebar.selectbox("Customer Segment", segments)
        if selected_segment != 'All':
            optimized_df = optimized_df[optimized_df['customer_segment'] == selected_segment]
    
    # Utilization threshold
    util_threshold = st.sidebar.slider(
        "Utilization Threshold (%)",
        min_value=0,
        max_value=100,
        value=50,
        help="Highlight vehicles below this utilization"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Use filters to explore different scenarios and insights")
    
    # ============================================================
    # TAB LAYOUT
    # ============================================================
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", 
        "🚛 Vehicle Analytics", 
        "💰 Cost Analysis",
        "🌍 Sustainability",
        "📊 Performance Metrics"
    ])
    
    # ============================================================
    # TAB 1: OVERVIEW
    # ============================================================
    
    with tab1:
        st.header("Key Performance Indicators")
        
        # Debug info
        with st.expander("🔍 Debug Info - Click to expand"):
            st.write("**Dataset Info:**")
            st.write(f"- Shape: {optimized_df.shape}")
            st.write(f"- Columns: {len(optimized_df.columns)}")
            st.write(f"- Sample columns: {list(optimized_df.columns[:10])}")
            
            st.write("**Key Columns Check:**")
            key_cols = ['total_cost_inr', 'load_utilization_ratio', 'total_emissions_kg', 'vehicle_id']
            for col in key_cols:
                exists = col in optimized_df.columns
                if exists:
                    null_count = optimized_df[col].isna().sum()
                    st.write(f"✅ {col}: {null_count} nulls")
                else:
                    st.write(f"❌ {col}: NOT FOUND")
        
        # KPI Row with better error handling
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_orders = len(optimized_df)
            st.metric(
                label="Total Orders", 
                value=f"{total_orders:,}",
                help="Total number of orders in the dataset"
            )
        
        with col2:
            total_cost = optimized_df['total_cost_inr'].sum()
            st.metric(
                label="Total Cost", 
                value=f"₹{total_cost:,.0f}",
                help="Sum of all operational costs"
            )
        
        with col3:
            avg_util = optimized_df['load_utilization_ratio'].mean()
            delta_val = avg_util - 50
            st.metric(
                label="Avg Utilization", 
                value=f"{avg_util:.1f}%",
                delta=f"{delta_val:.1f}%",
                delta_color="normal",
                help="Average load utilization across all orders"
            )
        
        with col4:
            total_emissions = optimized_df['total_emissions_kg'].sum()
            st.metric(
                label="Total CO₂", 
                value=f"{total_emissions:,.0f} kg",
                help="Total carbon dioxide emissions"
            )
        
        with col5:
            unique_vehicles = optimized_df['vehicle_id'].nunique()
            st.metric(
                label="Vehicles Used", 
                value=f"{unique_vehicles}",
                help="Number of unique vehicles assigned"
            )
        
        st.markdown("---")
        
        # Fallback: Display KPIs as HTML if Streamlit metrics fail
        if st.checkbox("Use Alternative KPI Display", value=False):
            st.markdown("""
                <div style='display: flex; gap: 1rem; margin-bottom: 2rem;'>
                    <div style='flex: 1; background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #e0e0e0;'>
                        <div style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>Total Orders</div>
                        <div style='color: #262730; font-size: 2rem; font-weight: bold;'>{}</div>
                    </div>
                    <div style='flex: 1; background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #e0e0e0;'>
                        <div style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>Total Cost</div>
                        <div style='color: #262730; font-size: 2rem; font-weight: bold;'>₹{:,.0f}</div>
                    </div>
                    <div style='flex: 1; background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #e0e0e0;'>
                        <div style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>Avg Utilization</div>
                        <div style='color: #262730; font-size: 2rem; font-weight: bold;'>{:.1f}%</div>
                    </div>
                    <div style='flex: 1; background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #e0e0e0;'>
                        <div style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>Total CO₂</div>
                        <div style='color: #262730; font-size: 2rem; font-weight: bold;'>{:,.0f} kg</div>
                    </div>
                    <div style='flex: 1; background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #e0e0e0;'>
                        <div style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>Vehicles Used</div>
                        <div style='color: #262730; font-size: 2rem; font-weight: bold;'>{}</div>
                    </div>
                </div>
            """.format(
                len(optimized_df),
                optimized_df['total_cost_inr'].sum(),
                optimized_df['load_utilization_ratio'].mean(),
                optimized_df['total_emissions_kg'].sum(),
                optimized_df['vehicle_id'].nunique()
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📦 Orders by Priority")
            if 'priority' in optimized_df.columns:
                priority_counts = optimized_df['priority'].value_counts()
                fig = px.pie(
                    values=priority_counts.values,
                    names=priority_counts.index,
                    title="Distribution of Order Priorities",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🏷️ Orders by Product Category")
            if 'product_category' in optimized_df.columns:
                category_counts = optimized_df['product_category'].value_counts().head(10)
                fig = px.bar(
                    x=category_counts.values,
                    y=category_counts.index,
                    orientation='h',
                    title="Top 10 Product Categories",
                    labels={'x': 'Number of Orders', 'y': 'Category'},
                    color=category_counts.values,
                    color_continuous_scale='Blues'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Utilization Distribution")
            if 'load_utilization_ratio' in optimized_df.columns:
                fig = px.histogram(
                    optimized_df,
                    x='load_utilization_ratio',
                    nbins=30,
                    title="Load Utilization Distribution",
                    labels={'load_utilization_ratio': 'Utilization (%)'},
                    color_discrete_sequence=['#1f77b4']
                )
                fig.add_vline(x=50, line_dash="dash", line_color="red", 
                             annotation_text="50% Threshold")
                fig.add_vline(x=100, line_dash="dash", line_color="orange",
                             annotation_text="100% Capacity")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💵 Cost Breakdown")
            if all(col in optimized_df.columns for col in ['fuel_cost', 'labor_cost', 'vehicle_maintenance']):
                cost_components = {
                    'Fuel': optimized_df['fuel_cost'].sum(),
                    'Labor': optimized_df['labor_cost'].sum(),
                    'Maintenance': optimized_df['vehicle_maintenance'].sum(),
                }
                if 'packaging_cost' in optimized_df.columns:
                    cost_components['Packaging'] = optimized_df['packaging_cost'].sum()
                if 'insurance' in optimized_df.columns:
                    cost_components['Insurance'] = optimized_df['insurance'].sum()
                
                fig = px.pie(
                    values=list(cost_components.values()),
                    names=list(cost_components.keys()),
                    title="Cost Components Breakdown",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ============================================================
    # TAB 2: VEHICLE ANALYTICS
    # ============================================================
    
    with tab2:
        st.header("Vehicle Performance Analysis")
        
        # Vehicle summary
        if 'vehicle_id' in optimized_df.columns:
            vehicle_summary = optimized_df.groupby('vehicle_id').agg({
                'order_id': 'count',
                'load_utilization_ratio': ['mean', 'min', 'max'],
                'distance_km': 'sum',
                'total_cost_inr': 'sum',
                'total_emissions_kg': 'sum'
            }).round(2)
            
            vehicle_summary.columns = ['Orders', 'Avg_Util', 'Min_Util', 'Max_Util', 
                                      'Total_Distance', 'Total_Cost', 'Total_Emissions']
            vehicle_summary = vehicle_summary.sort_values('Avg_Util', ascending=False)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("🚛 Vehicle Utilization Heatmap")
                
                # Create heatmap data
                top_vehicles = vehicle_summary.head(20).reset_index()
                
                fig = go.Figure(data=go.Heatmap(
                    z=[top_vehicles['Avg_Util'].values],
                    x=top_vehicles['vehicle_id'].values,
                    y=['Utilization'],
                    colorscale='RdYlGn',
                    text=[top_vehicles['Avg_Util'].values],
                    texttemplate='%{text:.1f}%',
                    textfont={"size": 10},
                    colorbar=dict(title="Utilization %")
                ))
                
                fig.update_layout(
                    title="Top 20 Vehicles by Average Utilization",
                    xaxis_title="Vehicle ID",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Vehicle Stats")
                
                underutilized = (vehicle_summary['Avg_Util'] < util_threshold).sum()
                optimal = ((vehicle_summary['Avg_Util'] >= 50) & 
                          (vehicle_summary['Avg_Util'] <= 90)).sum()
                overloaded = (vehicle_summary['Avg_Util'] > 100).sum()
                
                st.metric("Underutilized", underutilized, 
                         delta=f"{(underutilized/len(vehicle_summary)*100):.1f}%")
                st.metric("Optimal", optimal,
                         delta=f"{(optimal/len(vehicle_summary)*100):.1f}%")
                st.metric("Overloaded", overloaded,
                         delta=f"{(overloaded/len(vehicle_summary)*100):.1f}%")
            
            # Detailed vehicle table
            st.subheader("📋 Detailed Vehicle Report")
            
            # Add status column
            def get_status(util):
                if util < 50:
                    return "🔴 Underutilized"
                elif util > 100:
                    return "🟠 Overloaded"
                else:
                    return "🟢 Optimal"
            
            vehicle_summary['Status'] = vehicle_summary['Avg_Util'].apply(get_status)
            
            st.dataframe(
                vehicle_summary.style.background_gradient(
                    subset=['Avg_Util'], 
                    cmap='RdYlGn',
                    vmin=0,
                    vmax=100
                ),
                use_container_width=True
            )
            
            # Download button
            csv = vehicle_summary.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Download Vehicle Report",
                data=csv,
                file_name="vehicle_summary.csv",
                mime="text/csv"
            )
    
    # ============================================================
    # TAB 3: COST ANALYSIS
    # ============================================================
    
    with tab3:
        st.header("Cost Analysis Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'fuel_cost' in optimized_df.columns:
                total_fuel = optimized_df['fuel_cost'].sum()
                avg_fuel = optimized_df['fuel_cost'].mean()
                st.metric("Total Fuel Cost", f"₹{total_fuel:,.0f}")
                st.caption(f"Avg per order: ₹{avg_fuel:.2f}")
        
        with col2:
            if 'total_cost_inr' in optimized_df.columns:
                total_cost = optimized_df['total_cost_inr'].sum()
                avg_cost = optimized_df['total_cost_inr'].mean()
                st.metric("Total Operating Cost", f"₹{total_cost:,.0f}")
                st.caption(f"Avg per order: ₹{avg_cost:.2f}")
        
        with col3:
            if 'distance_km' in optimized_df.columns and 'fuel_cost' in optimized_df.columns:
                cost_per_km = optimized_df['fuel_cost'].sum() / optimized_df['distance_km'].sum()
                st.metric("Cost per KM", f"₹{cost_per_km:.2f}")
        
        st.markdown("---")
        
        # Cost trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Cost vs Distance")
            if 'distance_km' in optimized_df.columns and 'total_cost_inr' in optimized_df.columns:
                fig = px.scatter(
                    optimized_df,
                    x='distance_km',
                    y='total_cost_inr',
                    color='load_utilization_ratio',
                    size='order_value_inr' if 'order_value_inr' in optimized_df.columns else None,
                    title="Cost vs Distance (colored by utilization)",
                    labels={
                        'distance_km': 'Distance (km)',
                        'total_cost_inr': 'Total Cost (₹)',
                        'load_utilization_ratio': 'Utilization %'
                    },
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📦 Cost by Product Category")
            if 'product_category' in optimized_df.columns and 'total_cost_inr' in optimized_df.columns:
                category_cost = optimized_df.groupby('product_category')['total_cost_inr'].sum().sort_values(ascending=False).head(10)
                fig = px.bar(
                    x=category_cost.values,
                    y=category_cost.index,
                    orientation='h',
                    title="Top 10 Categories by Total Cost",
                    labels={'x': 'Total Cost (₹)', 'y': 'Category'},
                    color=category_cost.values,
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Cost efficiency metrics
        st.subheader("⚡ Cost Efficiency Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'load_utilization_ratio' in optimized_df.columns and 'fuel_cost' in optimized_df.columns:
                # Efficient orders (high utilization, low cost)
                efficient = optimized_df[
                    (optimized_df['load_utilization_ratio'] >= 60) & 
                    (optimized_df['fuel_cost'] < optimized_df['fuel_cost'].median())
                ]
                st.metric("Efficient Orders", len(efficient),
                         delta=f"{len(efficient)/len(optimized_df)*100:.1f}%")
        
        with col2:
            if 'load_utilization_ratio' in optimized_df.columns and 'total_cost_inr' in optimized_df.columns:
                # Calculate cost per utilization point
                optimized_df['cost_per_util'] = optimized_df['total_cost_inr'] / optimized_df['load_utilization_ratio']
                avg_cost_util = optimized_df['cost_per_util'].mean()
                st.metric("Avg Cost per Util%", f"₹{avg_cost_util:.2f}")
        
        with col3:
            if 'fuel_consumption_l' in optimized_df.columns:
                total_fuel_liters = optimized_df['fuel_consumption_l'].sum()
                st.metric("Total Fuel Consumed", f"{total_fuel_liters:,.0f} L")
    
    # ============================================================
    # TAB 4: SUSTAINABILITY
    # ============================================================
    
    with tab4:
        st.header("Environmental Impact Analysis")
        
        if 'total_emissions_kg' in optimized_df.columns:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_co2 = optimized_df['total_emissions_kg'].sum()
                st.metric("Total CO₂ Emissions", f"{total_co2:,.0f} kg")
            
            with col2:
                avg_co2 = optimized_df['total_emissions_kg'].mean()
                st.metric("Avg CO₂ per Order", f"{avg_co2:.2f} kg")
            
            with col3:
                if 'distance_km' in optimized_df.columns:
                    co2_per_km = total_co2 / optimized_df['distance_km'].sum()
                    st.metric("CO₂ per KM", f"{co2_per_km:.3f} kg")
            
            with col4:
                # Trees needed to offset (1 tree absorbs ~21 kg CO2/year)
                trees_needed = total_co2 / 21
                st.metric("Trees to Offset", f"{trees_needed:,.0f}")
            
            st.markdown("---")
            
            # Emissions analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🌱 Emissions by Vehicle Type")
                if 'vehicle_type' in optimized_df.columns:
                    veh_emissions = optimized_df.groupby('vehicle_type')['total_emissions_kg'].sum().sort_values(ascending=False)
                    fig = px.bar(
                        x=veh_emissions.index,
                        y=veh_emissions.values,
                        title="CO₂ Emissions by Vehicle Type",
                        labels={'x': 'Vehicle Type', 'y': 'Total CO₂ (kg)'},
                        color=veh_emissions.values,
                        color_continuous_scale='Greens_r'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Distance vs Emissions")
                fig = px.scatter(
                    optimized_df,
                    x='distance_km',
                    y='total_emissions_kg',
                    color='vehicle_type' if 'vehicle_type' in optimized_df.columns else None,
                    title="Distance vs CO₂ Emissions",
                    labels={
                        'distance_km': 'Distance (km)',
                        'total_emissions_kg': 'CO₂ Emissions (kg)'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Fuel efficiency
            st.subheader("⛽ Fuel Efficiency Analysis")
            
            if 'fuel_efficiency_km_per_l' in optimized_df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.histogram(
                        optimized_df,
                        x='fuel_efficiency_km_per_l',
                        nbins=30,
                        title="Fuel Efficiency Distribution",
                        labels={'fuel_efficiency_km_per_l': 'KM per Liter'},
                        color_discrete_sequence=['#2ca02c']
                    )
                    avg_eff = optimized_df['fuel_efficiency_km_per_l'].mean()
                    fig.add_vline(x=avg_eff, line_dash="dash", line_color="red",
                                 annotation_text=f"Avg: {avg_eff:.2f}")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'vehicle_type' in optimized_df.columns:
                        veh_eff = optimized_df.groupby('vehicle_type')['fuel_efficiency_km_per_l'].mean().sort_values(ascending=False)
                        fig = px.bar(
                            x=veh_eff.values,
                            y=veh_eff.index,
                            orientation='h',
                            title="Average Fuel Efficiency by Vehicle Type",
                            labels={'x': 'KM per Liter', 'y': 'Vehicle Type'},
                            color=veh_eff.values,
                            color_continuous_scale='Greens'
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    # ============================================================
    # TAB 5: PERFORMANCE METRICS
    # ============================================================
    
    with tab5:
        st.header("Delivery Performance Metrics")
        
        # Always show metrics section
        col1, col2, col3, col4 = st.columns(4)
        
        if 'delivery_status' in optimized_df.columns:
            status_counts = optimized_df['delivery_status'].value_counts()
            
            with col1:
                on_time = status_counts.get('On-Time', 0)
                on_time_pct = (on_time / len(optimized_df)) * 100
                st.metric("On-Time Deliveries", on_time, delta=f"{on_time_pct:.1f}%")
            
            with col2:
                slightly_delayed = status_counts.get('Slightly-Delayed', 0)
                st.metric("Slightly Delayed", slightly_delayed)
            
            with col3:
                severely_delayed = status_counts.get('Severely-Delayed', 0)
                st.metric("Severely Delayed", severely_delayed)
            
            with col4:
                avg_delay = optimized_df['delivery_delay_days'].mean()
                st.metric("Avg Delay (days)", f"{avg_delay:.2f}")
        else:
            with col1:
                st.warning("Delivery status data not available")
            with col2:
                st.info("Load complete dataset")
            with col3:
                st.info("Check data pipeline")
            with col4:
                st.info("Missing columns")
            
            st.markdown("---")
            
            # Performance charts - Always render containers
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📦 Delivery Status Distribution")
                if len(status_counts) > 0:
                    fig = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Delivery Status Breakdown",
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No delivery status data available")
            
            with col2:
                st.subheader("⏱️ Delivery Time Analysis")
                if 'promised_delivery_days' in optimized_df.columns and 'actual_delivery_days' in optimized_df.columns:
                    # Filter out NaN values
                    plot_df = optimized_df.dropna(subset=['promised_delivery_days', 'actual_delivery_days'])
                    
                    if len(plot_df) > 0:
                        fig = px.scatter(
                            plot_df,
                            x='promised_delivery_days',
                            y='actual_delivery_days',
                            color='delivery_status' if 'delivery_status' in plot_df.columns else None,
                            title="Promised vs Actual Delivery Days",
                            labels={
                                'promised_delivery_days': 'Promised (days)',
                                'actual_delivery_days': 'Actual (days)'
                            }
                        )
                        # Add diagonal line (perfect delivery)
                        max_days = max(plot_df['promised_delivery_days'].max(), 
                                      plot_df['actual_delivery_days'].max())
                        fig.add_trace(go.Scatter(
                            x=[0, max_days],
                            y=[0, max_days],
                            mode='lines',
                            line=dict(dash='dash', color='red'),
                            name='Perfect Delivery',
                            showlegend=True
                        ))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No valid delivery time data")
                else:
                    st.info("Delivery time columns not available")
        
        # Quality metrics - Always render section
        st.subheader("✅ Quality & Customer Satisfaction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'quality_issue' in optimized_df.columns:
                quality_counts = optimized_df['quality_issue'].value_counts()
                
                if len(quality_counts) > 0:
                    fig = px.bar(
                        x=quality_counts.index,
                        y=quality_counts.values,
                        title="Distribution of Quality Issues",
                        labels={'x': 'Issue Type', 'y': 'Count'},
                        color=quality_counts.values,
                        color_continuous_scale='Reds_r'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No quality issue data available")
            else:
                st.warning("Quality issue column not found")
        
        with col2:
            if 'customer_rating' in optimized_df.columns:
                # Filter out NaN ratings
                rating_df = optimized_df.dropna(subset=['customer_rating'])
                
                if len(rating_df) > 0:
                    avg_rating = rating_df['customer_rating'].mean()
                    rating_dist = rating_df['customer_rating'].value_counts().sort_index()
                    
                    fig = px.bar(
                        x=rating_dist.index,
                        y=rating_dist.values,
                        title=f"Customer Ratings (Avg: {avg_rating:.2f})",
                        labels={'x': 'Rating', 'y': 'Count'},
                        color=rating_dist.index,
                        color_continuous_scale='RdYlGn'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No customer rating data available")
            else:
                st.warning("Customer rating column not found")
        
        # Route efficiency - Always render section
        st.subheader("🚦 Traffic Impact Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'traffic_delay_minutes' in optimized_df.columns:
                # Filter out NaN values
                delay_df = optimized_df.dropna(subset=['traffic_delay_minutes'])
                
                if len(delay_df) > 0:
                    avg_delay = delay_df['traffic_delay_minutes'].mean()
                    total_delay = delay_df['traffic_delay_minutes'].sum()
                    
                    st.metric("Total Traffic Delay", f"{total_delay:,.0f} min",
                             delta=f"{total_delay/60:.1f} hours")
                    st.metric("Avg Delay per Order", f"{avg_delay:.1f} min")
                else:
                    st.info("No traffic delay data available")
            else:
                st.warning("Traffic delay column not found")
        
        with col2:
            if 'traffic_delay_minutes' in optimized_df.columns:
                delay_df = optimized_df.dropna(subset=['traffic_delay_minutes'])
                
                if len(delay_df) > 0:
                    fig = px.histogram(
                        delay_df,
                        x='traffic_delay_minutes',
                        nbins=30,
                        title="Traffic Delay Distribution",
                        labels={'traffic_delay_minutes': 'Delay (minutes)'},
                        color_discrete_sequence=['#ff7f0e']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No traffic delay data to plot")
            else:
                st.info("Traffic delay data not available")

# ============================================================
# RUN APP
# ============================================================

if __name__ == "__main__":
    main()