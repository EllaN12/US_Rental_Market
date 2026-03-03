#%%
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

st.set_page_config(
    page_title="Rental Clusters - Amenities Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS
st.markdown("""
<style>
    .main {background-color: #1a1f2e;}
    [data-testid="stSidebar"] {background-color: #252936;}
    h1, h2, h3 {color: #ffffff !important;}
    p, label {color: #e0e0e0 !important;}
    
    .stButton button {
        background-color: #505050;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton button:hover {
        background-color: #666666;
    }
</style>
""", unsafe_allow_html=True)

# Load data with error handling
@st.cache_data
def load_data():
    try:
        data_path = Path(__file__).resolve().parent.parent / "Output" / "final_data.csv"
        if not data_path.exists():
            st.error(f"Dataset not found at: {data_path}")
            st.stop()
        
        df = pd.read_csv(data_path)
        
        # Validate columns
        required_cols = ['latitude', 'longitude', 'prediction_label', 'price', 
                        'square_feet', 'sports_count', 'outdoor_count', 
                        'luxury_count', 'convenience_count', 'cityname', 'state']
        
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
            st.stop()
        
        # Add cluster names
        df['cluster_name'] = df['prediction_label'].map({
            0: 'Essential Rentals',
            1: 'Amenity-Packed Rentals'
        })
        
        # Calculate derived fields
        df['total_amenities'] = (
            df['sports_count'] + df['outdoor_count'] + 
            df['luxury_count'] + df['convenience_count']
        )
        
        df['price_per_sqft'] = df['price'] / df['square_feet']
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

df = load_data()

# Initialize session state for reset functionality
if 'reset_trigger' not in st.session_state:
    st.session_state.reset_trigger = 0

# Title
st.markdown("""
    <h1 style='text-align: center; padding: 20px;'>
        Rental Property Clusters - Amenities Analysis
    </h1>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎛️ FILTERS")
    st.markdown("---")
    
    # State filter
    states = ['All'] + sorted(df['state'].unique().tolist())
    selected_state = st.selectbox(
        "State", 
        states, 
        index=0,
        key=f"state_{st.session_state.reset_trigger}"
    )
    
    # City filter
    if selected_state == 'All':
        cities = ['All'] + sorted(df['cityname'].unique().tolist())
    else:
        cities = ['All'] + sorted(
            df[df['state'] == selected_state]['cityname'].unique().tolist()
        )
    selected_city = st.selectbox(
        "City", 
        cities, 
        index=0,
        key=f"city_{st.session_state.reset_trigger}"
    )
    
    # Cluster filter
    clusters = st.multiselect(
        "Clusters",
        [0, 1],
        default=[0, 1],
        format_func=lambda x: f"Cluster {x} ({'Essential Rentals' if x==0 else 'Amenity-Packed Rentals'})",
        key=f"clusters_{st.session_state.reset_trigger}"
    )
    
    st.markdown("---")
    
    # Price range filter
    st.markdown("### 💰 Price Range")
    price_min, price_max = st.slider(
        "Select range",
        int(df['price'].min()),
        int(df['price'].max()),
        (int(df['price'].min()), int(df['price'].max())),
        step=50,
        key=f"price_{st.session_state.reset_trigger}"
    )
    
    st.markdown("---")
    
    # Reset button with session state
    if st.button("🔄 Reset Filters", use_container_width=True):
        st.session_state.reset_trigger += 1
        st.rerun()
    
    st.markdown("---")
    
    # Filter data
    filtered_df = df.copy()
    
    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['state'] == selected_state]
    
    if selected_city != 'All':
        filtered_df = filtered_df[filtered_df['cityname'] == selected_city]
    
    if clusters:
        filtered_df = filtered_df[filtered_df['prediction_label'].isin(clusters)]
    
    filtered_df = filtered_df[
        (filtered_df['price'] >= price_min) & 
        (filtered_df['price'] <= price_max)
    ]
    
    # STATISTICS
    st.markdown("## 📊 STATS")
    st.markdown("---")
    
    for cluster_id in sorted(clusters):
        cluster_data = filtered_df[filtered_df['prediction_label'] == cluster_id]
        
        if len(cluster_data) == 0:
            continue
        
        cluster_name = "Essential Rentals" if cluster_id == 0 else "Amenity-Packed Rentals"
        
        st.markdown(f"### {cluster_name}")
        st.markdown(f"""
**Properties:** {len(cluster_data):,}  

**Avg Price:** ${cluster_data['price'].mean():,.0f}  

**Avg Sq Ft:** {cluster_data['square_feet'].mean():,.0f}  

**Price/SqFt:** ${cluster_data['price'].mean() / cluster_data['square_feet'].mean():.2f}  

**Amenities:**  
- Sports: {cluster_data['sports_count'].mean():.2f}  
- Outdoor: {cluster_data['outdoor_count'].mean():.2f}  
- Luxury: {cluster_data['luxury_count'].mean():.2f}  
- Convenience: {cluster_data['convenience_count'].mean():.2f}  

**Total:** {cluster_data['total_amenities'].mean():.2f}
        """)
        st.markdown("---")

# Main content
location_text = "All Locations"
if selected_city != "All":
    location_text = f"{selected_city}, {selected_state}"
elif selected_state != "All":
    location_text = selected_state

# Map function with fixes
def scatter_map_(df, selected_state=None, selected_city=None):
    df = df.copy()
    
    if 'total_amenities' not in df.columns:
        df['total_amenities'] = (
            df['sports_count'] + df['outdoor_count'] + 
            df['luxury_count'] + df['convenience_count']
        )
    
    df['opacity'] = 0.7
    df['base_size'] = 4
    
    if selected_state and selected_state != 'All':
        df.loc[df['state'] != selected_state, 'opacity'] = 0.15
        df.loc[df['state'] != selected_state, 'base_size'] = 2
    
    if selected_city and selected_city != 'All':
        df.loc[df['cityname'] != selected_city, 'opacity'] = 0.1
        df.loc[df['cityname'] != selected_city, 'base_size'] = 1
    
    df['marker_size'] = df['total_amenities'] * 0.5 + df['base_size']
    
    fig = go.Figure()
    
    # Cluster 0 - Essential Rentals
    cluster0 = df[df['prediction_label'] == 0]
    if len(cluster0) > 0:
        fig.add_trace(go.Scattermapbox(
            lat=cluster0['latitude'],
            lon=cluster0['longitude'],
            mode='markers',
            marker=dict(
                size=cluster0['marker_size'],  
                color='#4dabf7',
                opacity=cluster0['opacity'],
                sizemode='diameter'
            ),
            customdata=cluster0[[
                'cityname', 'state', 'price', 'square_feet',
                'sports_count', 'outdoor_count', 'luxury_count', 
                'convenience_count', 'total_amenities', 'price_per_sqft'
            ]],
            hovertemplate=
                '<b>%{customdata[0]}, %{customdata[1]}</b><br>' +
                '<b>Essential Rentals</b><br><br>' +
                'Price: $%{customdata[2]:,.0f}<br>' +
                'Sq Ft: %{customdata[3]:,.0f}<br>' +
                '$/SqFt: $%{customdata[9]:.2f}<br><br>' +
                '<b>Amenities:</b><br>' +
                'Sports: %{customdata[4]:.0f} | Outdoor: %{customdata[5]:.0f}<br>' +
                'Luxury: %{customdata[6]:.0f} | Convenience: %{customdata[7]:.0f}<br>' +
                '<b>Total: %{customdata[8]:.0f}</b>' +
                '<extra></extra>',
            name='Essential Rentals'
        ))
    
    # Cluster 1 - Amenity-Packed Rentals
    cluster1 = df[df['prediction_label'] == 1]
    if len(cluster1) > 0:
        fig.add_trace(go.Scattermapbox(
            lat=cluster1['latitude'],
            lon=cluster1['longitude'],
            mode='markers',
            marker=dict(
                size=cluster1['marker_size'],
                color='#ff922b',
                opacity=cluster1['opacity'],
                sizemode='diameter'
            ),
            customdata=cluster1[[
                'cityname', 'state', 'price', 'square_feet',
                'sports_count', 'outdoor_count', 'luxury_count', 
                'convenience_count', 'total_amenities', 'price_per_sqft'
            ]],
            hovertemplate=
                '<b>%{customdata[0]}, %{customdata[1]}</b><br>' +
                '<b>Amenity-Packed Rentals</b><br><br>' +
                'Price: $%{customdata[2]:,.0f}<br>' +
                'Sq Ft: %{customdata[3]:,.0f}<br>' +
                '$/SqFt: $%{customdata[9]:.2f}<br><br>' +
                '<b>Amenities:</b><br>' +
                'Sports: %{customdata[4]:.0f} | Outdoor: %{customdata[5]:.0f}<br>' +
                'Luxury: %{customdata[6]:.0f} | Convenience: %{customdata[7]:.0f}<br>' +
                '<b>Total: %{customdata[8]:.0f}</b>' +
                '<extra></extra>',
            name='Amenity-Packed Rentals'
        ))
    
    fig.update_layout(
        mapbox=dict(
            style='carto-darkmatter',
            zoom=3.5,
            center=dict(lat=37.0902, lon=-95.7129)
        ),
        height=600,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor='#000000',
        plot_bgcolor='#000000',
        font=dict(color='#ffffff'),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0, 0, 0, 0.85)',
            bordercolor='#666666',
            borderwidth=1,
            x=0.02,
            y=0.02,
            xanchor='left',
            yanchor='bottom',
            font=dict(color='#ffffff', size=11),
            orientation='v',
            itemsizing='constant'
        ),
        hovermode='closest'
    )
    
    return fig

# Map display
st.markdown(f"### 🗺️ Property Distribution - {location_text}")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"*Showing: {len(filtered_df):,} properties | Price: ${price_min:,} - ${price_max:,}*")
with col2:
    st.markdown("*💡 Scroll to zoom, drag to pan*")

if len(filtered_df) > 0:
    map_fig = scatter_map_(filtered_df, selected_state, selected_city)
    st.plotly_chart(map_fig, use_container_width=True)
else:
    st.warning("No properties match the selected filters.")

st.markdown("---")

# Key Insights
st.markdown("### 💡 Key Insights")

if len(filtered_df) > 0:
    col1, col2, col3 = st.columns(3)
    
    budget_count = len(filtered_df[filtered_df['prediction_label'] == 0])
    premium_count = len(filtered_df[filtered_df['prediction_label'] == 1])
    
    with col1:
        st.metric(
            "Total Properties",
            f"{len(filtered_df):,}",
            f"Essential: {budget_count:,} | Amenity-Packed: {premium_count:,}"
        )
    
    with col2:
        if budget_count > 0 and premium_count > 0:
            budget_avg = filtered_df[filtered_df['prediction_label'] == 0]['price'].mean()
            premium_avg = filtered_df[filtered_df['prediction_label'] == 1]['price'].mean()
            diff = premium_avg - budget_avg
            st.metric(
                "Price Difference",
                f"${abs(diff):,.0f}",
                "Amenity-Packed vs Essential"
            )
        else:
            st.metric("Price Difference", "N/A")
    
    with col3:
        amenity_totals = {
            'Sports': filtered_df['sports_count'].sum(),
            'Outdoor': filtered_df['outdoor_count'].sum(),
            'Luxury': filtered_df['luxury_count'].sum(),
            'Convenience': filtered_df['convenience_count'].sum()
        }
        if sum(amenity_totals.values()) > 0:
            top_amenity = max(amenity_totals, key=amenity_totals.get)
            st.metric(
                "Top Amenity",
                top_amenity,
                f"{amenity_totals[top_amenity]:,.0f} total"
            )
        else:
            st.metric("Top Amenity", "None")

st.markdown("---")

# Pie charts
st.markdown(f"### 🥧 Amenity Composition by Cluster - {location_text}")

if len(filtered_df) > 0:
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'pie'}, {'type': 'pie'}]],
        subplot_titles=[
            f"<b>Essential Rentals</b><br><sup>{len(filtered_df[filtered_df['prediction_label']==0]):,} properties</sup>",
            f"<b>Amenity-Packed Rentals</b><br><sup>{len(filtered_df[filtered_df['prediction_label']==1]):,} properties</sup>"
        ]
    )
    
    colors = ['#51cf66', '#22b8cf', '#cc5de8', '#ff6b6b']
    
    for idx, cluster_id in enumerate([0, 1]):
        cluster_data = filtered_df[filtered_df['prediction_label'] == cluster_id]
        
        if len(cluster_data) > 0:
            values = [
                cluster_data['sports_count'].sum(),
                cluster_data['outdoor_count'].sum(),
                cluster_data['luxury_count'].sum(),
                cluster_data['convenience_count'].sum()
            ]
            
            if sum(values) > 0:  # ← FIXED: Only add if has amenities
                fig.add_trace(
                    go.Pie(
                        labels=['Sports', 'Outdoor', 'Luxury', 'Convenience'],
                        values=values,
                        marker=dict(colors=colors),
                        textfont=dict(color='white', size=12),
                        textposition='inside',
                        textinfo='label+percent'
                    ),
                    row=1, col=idx+1
                )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='#2b2b2b',
        plot_bgcolor='#2b2b2b',
        font=dict(color='#ffffff'),
        showlegend=True,
        legend=dict(bgcolor='#363636', bordercolor='#666666', borderwidth=1)
    )
    
    fig.update_annotations(font=dict(color='#ffffff', size=14))  # ← FIXED: Better titles
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Download section
st.markdown("### 💾 Download Data")

col1, col2, col3 = st.columns(3)

with col1:
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Filtered Data (CSV)",
        data=csv,
        file_name=f"rentals_{location_text.replace(', ', '_').replace(' ', '_')}.csv",
        mime="text/csv"
    )

with col2:
    # Summary stats
    stats_list = []
    for cluster_id in [0, 1]:
        cluster_data = filtered_df[filtered_df['prediction_label'] == cluster_id]
        if len(cluster_data) > 0:
            stats_list.append({
                'Cluster': 'Essential Rentals' if cluster_id == 0 else 'Amenity-Packed Rentals',
                'Properties': len(cluster_data),
                'Avg_Price': round(cluster_data['price'].mean(), 2),
                'Avg_SqFt': round(cluster_data['square_feet'].mean(), 2),
                'Avg_Sports': round(cluster_data['sports_count'].mean(), 2),
                'Avg_Outdoor': round(cluster_data['outdoor_count'].mean(), 2),
                'Avg_Luxury': round(cluster_data['luxury_count'].mean(), 2),
                'Avg_Convenience': round(cluster_data['convenience_count'].mean(), 2),
            })
    
    if stats_list:
        stats_csv = pd.DataFrame(stats_list).to_csv(index=False)
        st.download_button(
            label="📊 Statistics (CSV)",
            data=stats_csv,
            file_name=f"stats_{location_text.replace(', ', '_').replace(' ', '_')}.csv",
            mime="text/csv"
        )

with col3:
    st.info(f"""
    **Current Selection:**
    
    📍 {location_text}
    
    💰 ${price_min:,} - ${price_max:,}
    
    📊 {len(filtered_df):,} properties
    """)

st.markdown("---")

# Amenity definitions (enhanced)
with st.expander("📋 Amenity Type Definitions", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🏃 SPORTS AMENITIES** (Green)
        - Gym 
        - Basketball 
        - Tennis
        - Golf
        
        
        ---
        
        **🌳 OUTDOOR AMENITIES** (Sky Blue)
        - Clubhouse
        - Patio / Garden areas
        - Playground
        
        """)
    
    with col2:
        st.markdown("""
        **💎 LUXURY AMENITIES** (Purple)
        - Wood Floors
        - Fireplace
        - View
        - Doorman
        - Luxury
        - Hot Tub
        
        ---
        
        **🏠 CONVENIENCE AMENITIES** (Red)
        - Washer Dryer
        - Dishwasher
        - Refrigerator
        - Parking
        - Garbage Disposal
        - Storage
        - Gated
        - Refrigerator
        - Cable or Satellite
        - Internet Access
        """)
# %%
