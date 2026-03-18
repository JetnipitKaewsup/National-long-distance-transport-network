"""
Energy consumption model for drones
"""
from typing import Dict

class EnergyModel:
    """Model for energy consumption"""
    
    def __init__(self):
        self.consumption_rates = {
            'idle': 0.5,      # units per second
            'patrol': 1.0,
            'mesh_relay': 1.5,
            'transmit': 2.0,
            'receive': 1.2,
            'charge': -10.0    # negative = charging
        }
        
    def calculate_consumption(self, activity: str, duration: float) -> float:
        """Calculate energy consumption for activity"""
        rate = self.consumption_rates.get(activity, 1.0)
        return rate * duration
    
    def get_battery_lifetime(self, battery_capacity: float,
                            activities: Dict[str, float]) -> float:
        """Estimate battery lifetime given activity mix"""
        total_rate = 0
        for activity, proportion in activities.items():
            rate = self.consumption_rates.get(activity, 1.0)
            total_rate += rate * proportion
        
        if total_rate <= 0:
            return float('inf')
        
        return battery_capacity / total_rate
    
    def estimate_range(self, battery_capacity: float, speed: float,
                      activity: str = 'patrol') -> float:
        """Estimate travel range"""
        rate = self.consumption_rates.get(activity, 1.0)
        flight_time = battery_capacity / rate
        return flight_time * speed