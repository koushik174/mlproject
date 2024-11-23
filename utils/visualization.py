
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Dict, Any

class VisualizationManager:
    def __init__(self):
        self.default_height = 600
        self.default_width = 800
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'accent': '#2ca02c',
            'background': '#f0f2f6'
        }

    def create_visualization(self, data: pd.DataFrame, viz_type: str, **kwargs) -> go.Figure:
        """Create visualization based on data and type"""
        viz_functions = {
            "vessel_map": self._create_vessel_map,
            "vessel_density": self._create_density_map,
            "speed_analysis": self._create_speed_analysis,
            "port_activity": self._create_port_activity,
            "vessel_type_distribution": self._create_vessel_type_distribution,
            "time_series": self._create_time_series,
            "route_analysis": self._create_route_analysis
        }
        
        if viz_type not in viz_functions:
            raise ValueError(f"Unsupported visualization type: {viz_type}")
            
        return viz_functions[viz_type](data, **kwargs)

    def _create_vessel_map(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create vessel movement map"""
        fig = go.Figure()

        # Add vessel trajectories
        fig.add_trace(go.Scattergeo(
            lon=data['longitude'],
            lat=data['latitude'],
            mode='lines+markers',
            line=dict(width=2, color=self.color_scheme['primary']),
            marker=dict(size=4),
            name='Vessel Track',
            hovertemplate=(
                '<b>Vessel:</b> %{customdata[0]}<br>'
                '<b>Time:</b> %{customdata[1]}<br>'
                '<b>Speed:</b> %{customdata[2]:.1f} knots<br>'
                '<b>Position:</b> (%{lat:.2f}, %{lon:.2f})'
            ),
            customdata=data[['vessel_name', 'timestamp', 'speed']].values
        ))

        # Update layout
        fig.update_layout(
            title=kwargs.get('title', 'Vessel Movements'),
            geo=dict(
                showland=True,
                showcountries=True,
                showocean=True,
                countrywidth=0.5,
                landcolor='rgb(243, 243, 243)',
                oceancolor='rgb(204, 229, 255)',
                projection_type='mercator'
            ),
            height=self.default_height,
            width=self.default_width
        )

        return fig

    def _create_density_map(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create vessel density heatmap"""
        fig = go.Figure(go.Densitymapbox(
            lat=data['latitude'],
            lon=data['longitude'],
            radius=10,
            colorscale='Viridis',
            hovertemplate='Count: %{z}<br>Position: (%{lat:.2f}, %{lon:.2f})'
        ))

        center_lat = data['latitude'].mean()
        center_lon = data['longitude'].mean()

        fig.update_layout(
            title=kwargs.get('title', 'Vessel Density Map'),
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=kwargs.get('zoom', 5)
            ),
            height=self.default_height,
            width=self.default_width
        )

        return fig

    def _create_speed_analysis(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create speed analysis visualization"""
        fig = go.Figure()

        # Add speed distribution histogram
        fig.add_trace(go.Histogram(
            x=data['speed'],
            nbinsx=30,
            name='Speed Distribution',
            marker_color=self.color_scheme['primary']
        ))

        # Add KDE line if specified
        if kwargs.get('show_kde', True):
            kde = self._calculate_kde(data['speed'])
            fig.add_trace(go.Scatter(
                x=kde['x'],
                y=kde['y'],
                name='Density',
                line=dict(color=self.color_scheme['secondary'])
            ))

        fig.update_layout(
            title=kwargs.get('title', 'Vessel Speed Analysis'),
            xaxis_title='Speed (knots)',
            yaxis_title='Count',
            height=self.default_height,
            width=self.default_width,
            bargap=0.1
        )

        return fig

    def _create_port_activity(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create port activity visualization"""
        # Group data by port and calculate metrics
        port_stats = data.groupby('port_name').agg({
            'mmsi': 'count',
            'departure_time': lambda x: (x - x.min()).mean()
        }).reset_index()

        fig = go.Figure()

        # Add bars for vessel count
        fig.add_trace(go.Bar(
            x=port_stats['port_name'],
            y=port_stats['mmsi'],
            name='Vessel Count',
            marker_color=self.color_scheme['primary']
        ))

        # Add line for average stay duration
        fig.add_trace(go.Scatter(
            x=port_stats['port_name'],
            y=port_stats['departure_time'],
            name='Avg Stay Duration',
            yaxis='y2',
            line=dict(color=self.color_scheme['secondary'])
        ))

        fig.update_layout(
            title=kwargs.get('title', 'Port Activity Analysis'),
            xaxis_title='Port',
            yaxis_title='Number of Vessels',
            yaxis2=dict(
                title='Average Stay Duration (hours)',
                overlaying='y',
                side='right'
            ),
            height=self.default_height,
            width=self.default_width
        )

        return fig

    def _create_vessel_type_distribution(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create vessel type distribution visualization"""
        type_counts = data['vessel_type'].value_counts()

        fig = go.Figure(data=[
            go.Pie(
                labels=type_counts.index,
                values=type_counts.values,
                hole=0.4,
                marker=dict(colors=px.colors.qualitative.Set3)
            )
        ])

        fig.update_layout(
            title=kwargs.get('title', 'Vessel Type Distribution'),
            height=self.default_height,
            width=self.default_width
        )

        return fig

    def _create_time_series(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create time series visualization"""
        fig = go.Figure()

        # Add time series line
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data[kwargs.get('y_column', 'speed')],
            mode='lines',
            name=kwargs.get('y_column', 'speed'),
            line=dict(color=self.color_scheme['primary'])
        ))

        # Add moving average if specified
        if kwargs.get('show_ma', True):
            window = kwargs.get('ma_window', 24)
            ma = data[kwargs.get('y_column', 'speed')].rolling(window=window).mean()
            fig.add_trace(go.Scatter(
                x=data['timestamp'],
                y=ma,
                mode='lines',
                name=f'{window}h Moving Average',
                line=dict(color=self.color_scheme['secondary'])
            ))

        fig.update_layout(
            title=kwargs.get('title', 'Time Series Analysis'),
            xaxis_title='Time',
            yaxis_title=kwargs.get('y_column', 'speed'),
            height=self.default_height,
            width=self.default_width
        )

        return fig

    def _create_route_analysis(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create route analysis visualization"""
        fig = go.Figure()

        # Add route lines
        for vessel in data['mmsi'].unique():
            vessel_data = data[data['mmsi'] == vessel].sort_values('timestamp')
            fig.add_trace(go.Scattergeo(
                lon=vessel_data['longitude'],
                lat=vessel_data['latitude'],
                mode='lines+markers',
                name=f'Vessel {vessel}',
                hovertemplate=(
                    '<b>Vessel:</b> %{customdata[0]}<br>'
                    '<b>Time:</b> %{customdata[1]}<br>'
                    '<b>Speed:</b> %{customdata[2]:.1f} knots'
                ),
                customdata=vessel_data[['vessel_name', 'timestamp', 'speed']].values
            ))

        fig.update_layout(
            title=kwargs.get('title', 'Route Analysis'),
            geo=dict(
                showland=True,
                showcountries=True,
                showocean=True,
                projection_type='mercator'
            ),
            height=self.default_height,
            width=self.default_width,
            showlegend=True
        )

        return fig

    def _calculate_kde(self, data: pd.Series) -> Dict[str, np.ndarray]:
        """Calculate Kernel Density Estimation"""
        from scipy.stats import gaussian_kde
        import numpy as np
        
        kde = gaussian_kde(data)
        x_range = np.linspace(data.min(), data.max(), 100)
        return {'x': x_range, 'y': kde(x_range)}

    def update_layout_theme(self, fig: go.Figure) -> go.Figure:
        """Update figure layout with consistent theme"""
        fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor=self.color_scheme['background'],
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=60, r=60, t=60, b=60)
        )
        return fig
