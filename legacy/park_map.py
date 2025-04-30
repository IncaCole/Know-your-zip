"""
Park map visualization for Miami-Dade County
"""

import plotly.graph_objects as go

def plot_county_regions():
    """
    Creates and returns a figure showing Miami-Dade County shape with region labels and statistics
    """
    # Approximate coordinates for Miami-Dade County corners
    county_shape = [
        [25.97, -80.14],  # North point
        [25.97, -80.87],  # Northwest point
        [25.13, -80.87],  # Southwest point
        [25.13, -80.14],  # Southeast point
        [25.97, -80.14]   # Close the shape
    ]
    
    # Create the base figure
    fig = go.Figure()
    
    # Add the county outline
    fig.add_trace(go.Scattergeo(
        lon=[point[1] for point in county_shape],
        lat=[point[0] for point in county_shape],
        mode='lines',
        line=dict(width=1, color='rgba(47, 69, 56, 0.3)'),  # Thinner, more transparent line
        fill='toself',
        fillcolor='rgba(144, 169, 144, 0.3)',  # Keeping the same fill color
        name='Miami-Dade County'
    ))
    
    # Add region labels with statistics
    region_labels = [
        dict(text="NE<br>118 (18%)", lat=25.85, lon=-80.20),  # Northeast
        dict(text="SE<br>77 (12%)", lat=25.25, lon=-80.20),   # Southeast
        dict(text="SW<br>452 (70%)", lat=25.25, lon=-80.75)   # Southwest
    ]
    
    for label in region_labels:
        fig.add_trace(go.Scattergeo(
            lon=[label['lon']],
            lat=[label['lat']],
            text=[label['text']],
            mode='text',
            textfont=dict(size=16, color='#2F4538', family='Arial Black'),  # Keeping text color the same
            name=label['text']
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Park Locations',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        showlegend=False,
        geo=dict(
            scope='usa',
            projection_scale=20,  # Zoom level
            center=dict(lat=25.55, lon=-80.5),  # Center of the map
            showland=True,
            landcolor='rgb(243, 243, 243)',
            showcoastlines=True,
            coastlinecolor='rgba(80, 80, 80, 0.2)',  # Making coastlines more transparent too
            showframe=False
        ),
        height=450,  # Reduced height to match other charts
        margin=dict(l=0, r=0, t=30, b=0)  # Reduced top margin
    )
    
    return fig 