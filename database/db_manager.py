
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class DatabaseManager:
    def __init__(self, connection_string: str):
        """Initialize database connection"""
        self.engine = create_engine(connection_string)
        self.create_tables()

    def create_tables(self):
        """Create necessary database tables"""
        with self.engine.connect() as conn:
            # Create vessels table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS vessels (
                    mmsi INTEGER PRIMARY KEY,
                    vessel_name TEXT,
                    vessel_type TEXT,
                    length REAL,
                    width REAL,
                    flag TEXT,
                    destination TEXT
                )
            """))

            # Create AIS positions table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ais_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mmsi INTEGER,
                    timestamp DATETIME,
                    latitude REAL,
                    longitude REAL,
                    speed REAL,
                    course REAL,
                    navigation_status TEXT,
                    FOREIGN KEY (mmsi) REFERENCES vessels(mmsi)
                )
            """))

    def load_sample_data(self) -> None:
        """Generate and load sample maritime data"""
        vessel_types = ['Container Ship', 'Bulk Carrier', 'Tanker', 'Passenger', 'Cargo']
        flags = ['US', 'UK', 'NL', 'DE', 'SG', 'CN', 'JP']
        
        # Generate sample vessels
        vessels = pd.DataFrame({
            'mmsi': range(100000000, 100000020),
            'vessel_name': [f'MARITIME_{i}' for i in range(20)],
            'vessel_type': np.random.choice(vessel_types, 20),
            'length': np.random.uniform(100, 400, 20),
            'width': np.random.uniform(20, 60, 20),
            'flag': np.random.choice(flags, 20),
            'destination': np.random.choice(['Rotterdam', 'Singapore', 'Shanghai'], 20)
        })

        # Save to database
        vessels.to_sql('vessels', self.engine, if_exists='replace', index=False)

        # Generate AIS positions
        positions = []
        start_time = datetime.now() - timedelta(days=7)
        
        for mmsi in vessels['mmsi']:
            for hour in range(168):  # One week of data
                positions.append({
                    'mmsi': mmsi,
                    'timestamp': start_time + timedelta(hours=hour),
                    'latitude': np.random.uniform(20, 50),
                    'longitude': np.random.uniform(-130, -70),
                    'speed': np.random.uniform(0, 20),
                    'course': np.random.uniform(0, 359),
                    'navigation_status': np.random.choice(['Under way', 'At anchor', 'Moored'])
                })

        positions_df = pd.DataFrame(positions)
        positions_df.to_sql('ais_positions', self.engine, if_exists='replace', index=False)

    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Execute SQL query and return results as DataFrame"""
        try:
            with self.engine.connect() as conn:
                return pd.read_sql_query(text(query), conn)
        except Exception as e:
            print(f"Query execution failed: {str(e)}")
            return None

    def get_vessel_info(self, mmsi: int) -> Dict:
        """Get detailed information about a specific vessel"""
        query = f"""
            SELECT v.*, 
                   COUNT(DISTINCT p.id) as position_count,
                   MAX(p.timestamp) as last_position
            FROM vessels v
            LEFT JOIN ais_positions p ON v.mmsi = p.mmsi
            WHERE v.mmsi = {mmsi}
            GROUP BY v.mmsi
        """
        result = self.execute_query(query)
        return result.iloc[0].to_dict() if not result.empty else None

    def get_recent_positions(self, hours: int = 24) -> pd.DataFrame:
        """Get vessel positions from the last n hours"""
        query = f"""
            SELECT v.vessel_name, v.vessel_type, p.*
            FROM ais_positions p
            JOIN vessels v ON p.mmsi = v.mmsi
            WHERE p.timestamp >= datetime('now', '-{hours} hours')
            ORDER BY p.timestamp DESC
        """
        return self.execute_query(query)
