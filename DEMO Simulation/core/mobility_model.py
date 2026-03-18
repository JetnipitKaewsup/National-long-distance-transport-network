"""
Mobility model for moving nodes
"""
import random
import math
from typing import Dict, List, Tuple, Optional
import numpy as np

class MobilityModel:
    """Model for node movement"""
    
    def __init__(self):
        self.vehicles = {}  # vehicle_id -> movement data
        self.waypoints = {}  # vehicle_id -> list of waypoints
        
    def add_vehicle(self, vehicle_id: str, start_pos: Tuple[float, float, float],
                   speed: float, waypoints: List[Tuple[float, float, float]] = None):
        """Add a moving vehicle"""
        if waypoints is None:
            # Generate random waypoints
            waypoints = self._generate_waypoints(start_pos)
        
        self.vehicles[vehicle_id] = {
            'position': start_pos,
            'speed': speed,
            'waypoints': waypoints,
            'current_wp': 0,
            'direction': random.uniform(0, 2 * math.pi)
        }
    
    def _generate_waypoints(self, start_pos: Tuple[float, float, float],
                           num_points: int = 3) -> List[Tuple[float, float, float]]:
        """Generate random waypoints"""
        waypoints = [start_pos]
        x, y, z = start_pos
        
        for _ in range(num_points):
            x += random.uniform(-500, 500)
            y += random.uniform(-500, 500)
            waypoints.append((x, y, z))
        
        return waypoints
    
    def update_positions(self, dt: float) -> Dict[str, Tuple[float, float, float]]:
        """Update positions of all vehicles"""
        updates = {}
        
        for vehicle_id, data in self.vehicles.items():
            # Get current target
            waypoints = data['waypoints']
            current_wp = data['current_wp']
            target = waypoints[current_wp]
            
            # Move towards target
            pos = data['position']
            new_pos = self._move_towards(pos, target, data['speed'], dt)
            data['position'] = new_pos
            updates[vehicle_id] = new_pos
            
            # Check if reached waypoint
            if self._distance(new_pos, target) < 10:
                data['current_wp'] = (current_wp + 1) % len(waypoints)
        
        return updates
    
    def _move_towards(self, current: Tuple[float, float, float],
                     target: Tuple[float, float, float],
                     speed: float, dt: float) -> Tuple[float, float, float]:
        """Move towards target position"""
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        dz = target[2] - current[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < speed * dt:
            return target
        
        ratio = (speed * dt) / distance
        return (
            current[0] + dx * ratio,
            current[1] + dy * ratio,
            current[2] + dz * ratio
        )
    
    def _distance(self, pos1: Tuple[float, float, float],
                 pos2: Tuple[float, float, float]) -> float:
        """Calculate distance between positions"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))
    
    def get_position(self, vehicle_id: str) -> Optional[Tuple[float, float, float]]:
        """Get vehicle position"""
        if vehicle_id in self.vehicles:
            return self.vehicles[vehicle_id]['position']
        return None
    
    def get_speed(self, vehicle_id: str) -> float:
        """Get vehicle speed"""
        if vehicle_id in self.vehicles:
            return self.vehicles[vehicle_id]['speed']
        return 0.0