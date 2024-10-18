import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def load_and_process_data(file_path):
    """Load and process the CSV file."""
    # Read CSV file
    df = pd.read_csv(file_path)
    
    # Convert date columns to datetime
    df['Sale Start date'] = pd.to_datetime(df['Sale Start date'])
    df['Sale End date'] = pd.to_datetime(df['Sale End date'])
    
    # Create month-year column for filtering
    df['Month-Year'] = df['Sale Start date'].dt.strftime('%Y-%m')
    
    return df

def calculate_metrics(df, selected_label='All', selected_period='All'):
    """Calculate key metrics based on filters."""
    # Apply filters
    filtered_df = df.copy()
    if selected_label != 'All':
        filtered_df = filtered_df[filtered_df['Reporting Label'] == selected_label]
    if selected_period != 'All':
        filtered_df = filtered_df[filtered_df['Month-Year'] == selected_period]
    
    # Calculate metrics
    total_earnings = filtered_df['Your Earnings'].sum()
    
    # DSP distribution
    dsp_earnings = filtered_df.groupby('Source')['Your Earnings'].sum()
    
    # Artist performance
    artist_earnings = filtered_df.groupby('Asset Artist')['Your Earnings'].sum()

    # Asset title performance
    asset_earnings = filtered_df.groupby('Product Title')['Your Earnings'].sum()

    return total_earnings, dsp_earnings, artist_earnings, asset_earnings

def create_dashboard():
    st.set_page_config(page_title="Digital Sales Dashboard", layout="wide")
    st.title("Digital Sales Dashboard")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    if uploaded_file is not None:
        df = load_and_process_data(uploaded_file)
        
        # Sidebar filters
        st.sidebar.header("Filters")
        labels = ['All'] + list(df['Reporting Label'].unique())
        periods = ['All'] + list(df['Month-Year'].unique())
        
        selected_label = st.sidebar.selectbox("Select Label", labels)
        selected_period = st.sidebar.selectbox("Select Period", periods)
        
        # Calculate metrics
        total_earnings, dsp_earnings, artist_earnings, asset_earnings = calculate_metrics(
            df, selected_label, selected_period
        )
        
        # Display metrics in columns
        col1 = st.columns(1)[0]
        
        with col1:
            st.metric("Total Earnings", f"${total_earnings:,.2f}")
        
        # DSP Distribution Chart
        st.subheader("DSP Distribution")
        fig_dsp = px.bar(
            x=dsp_earnings.index,
            y=dsp_earnings.values,
            labels={'x': 'DSP', 'y': 'Earnings ($)'},
            title="Earnings by DSP"
        )
        st.plotly_chart(fig_dsp, use_container_width=True)
        
        # Artist Performance
        st.subheader("Artist Performance")
        artist_df = pd.DataFrame({
            'Artist': artist_earnings.index,
            'Earnings': artist_earnings.values,
            'Percentage': (artist_earnings / total_earnings * 100).round(2)
        }).sort_values('Earnings', ascending=False)
        
        fig_artist = go.Figure(data=[
            go.Table(
                header=dict(
                    values=['Artist', 'Earnings', 'Percentage of Total'],
                    fill_color=None,
                    align='left'
                ),
                cells=dict(
                    values=[
                        artist_df['Artist'],
                        artist_df['Earnings'].apply(lambda x: f"${x:,.2f}"),
                        artist_df['Percentage'].apply(lambda x: f"{x}%")
                    ],
                    fill_color=None,
                    align='left'
                )
            )
        ])
        st.plotly_chart(fig_artist, use_container_width=True)

        # Asset Title Performance
        st.subheader("Asset Title Performance")
        asset_df = pd.DataFrame({
            'Asset Title': asset_earnings.index,
            'Earnings': asset_earnings.values,
            'Percentage': (asset_earnings / total_earnings * 100).round(2)
        }).sort_values('Earnings', ascending=False)

        fig_assets = go.Figure(data=[
            go.Table(
                header=dict(
                    values=['Asset Title', 'Earnings', 'Percentage of Total'],
                    fill_color=None,  # No background color for the header
                    align='left'
                ),
                cells=dict(
                    values=[
                        asset_df['Asset Title'],
                        asset_df['Earnings'].apply(lambda x: f"${x:,.2f}"),
                        asset_df['Percentage'].apply(lambda x: f"{x}%")
                    ],
                    fill_color=None,  # No background color for the cells
                    align='left'
                )
            )
        ])
        st.plotly_chart(fig_assets, use_container_width=True)

        # Monthly Trends
        st.subheader("Monthly Trends")
        monthly_earnings = df.groupby('Month-Year')['Your Earnings'].sum().reset_index()
        fig_trends = px.line(
            monthly_earnings,
            x='Month-Year',
            y='Your Earnings',
            title="Monthly Earnings Trend",
            labels={'Your Earnings': 'Earnings ($)', 'Month-Year': 'Period'}
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
        # Detailed Data View
        st.subheader("Detailed Data View")
        columns_to_display = [
            'Sale Start date', 'Source', 'Reporting Label',
            'Asset Artist', 'Product Title', 'Your Earnings'
        ]
        st.dataframe(
            df[columns_to_display].sort_values('Sale Start date', ascending=False),
            use_container_width=True
        )

if __name__ == "__main__":
    create_dashboard()
