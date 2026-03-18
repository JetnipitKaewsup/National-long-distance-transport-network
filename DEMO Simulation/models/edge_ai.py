"""
Edge AI models for anomaly detection and route optimization
"""
import numpy as np
import math
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import heapq

class AnomalyDetectionModel:
    """Detect anomalies in sensor data"""
    
    def __init__(self, threshold: float = 0.95):
        self.threshold = threshold
        self.baseline_patterns = {}
        self.anomaly_history = []
        
    def train(self, historical_data: List[Dict]):
        """Train on normal operation data"""
        for data_point in historical_data:
            sensor_type = data_point.get('sensor_type', 'unknown')
            value = data_point.get('value', 0)
            
            if sensor_type not in self.baseline_patterns:
                self.baseline_patterns[sensor_type] = {
                    'mean': value,
                    'std': 0,
                    'min': value,
                    'max': value,
                    'count': 1,
                    'values': [value]
                }
            else:
                baseline = self.baseline_patterns[sensor_type]
                values = baseline['values'] + [value]
                baseline['mean'] = np.mean(values)
                baseline['std'] = np.std(values) if len(values) > 1 else 0
                baseline['min'] = min(baseline['min'], value)
                baseline['max'] = max(baseline['max'], value)
                baseline['count'] += 1
                baseline['values'] = values[-100:]  # Keep last 100
    
    def detect(self, data: Dict) -> Dict:
        """Detect anomalies in sensor data"""
        sensor_type = data.get('sensor_type', 'unknown')
        value = data.get('value', 0)
        
        if sensor_type not in self.baseline_patterns:
            return {
                'is_anomaly': False,
                'anomaly_score': 0,
                'confidence': 0,
                'message': 'No baseline for this sensor'
            }
        
        baseline = self.baseline_patterns[sensor_type]
        
        if baseline['std'] > 0:
            # Z-score based detection
            z_score = abs(value - baseline['mean']) / baseline['std']
            is_anomaly = z_score > 3.0  # 3-sigma rule
            anomaly_score = min(1.0, z_score / 5.0)
            confidence = min(1.0, z_score / 4.0)
        else:
            # Range-based for constant values
            range_size = baseline['max'] - baseline['min']
            if range_size > 0:
                deviation = abs(value - baseline['mean']) / range_size
            else:
                deviation = abs(value - baseline['mean']) / (baseline['mean'] + 0.001)
            
            is_anomaly = deviation > 0.2
            anomaly_score = min(1.0, deviation * 2)
            confidence = min(1.0, deviation * 1.5)
        
        result = {
            'is_anomaly': is_anomaly,
            'anomaly_score': float(anomaly_score),
            'confidence': float(confidence),
            'expected_value': float(baseline['mean']),
            'sensor_type': sensor_type,
            'value': value
        }
        
        if is_anomaly:
            self.anomaly_history.append(result)
            if len(self.anomaly_history) > 100:
                self.anomaly_history.pop(0)
        
        return result
    
    def get_anomaly_rate(self) -> float:
        """Get anomaly detection rate"""
        if not self.anomaly_history:
            return 0.0
        return len(self.anomaly_history) / 100  # Normalized

class RouteOptimizationModel:
    """Optimize routes for emergency response"""
    
    def __init__(self):
        self.hazard_zones = []  # List of (center, radius, severity)
        self.route_cache = {}
        self.cache_timeout = 60  # seconds
        
    def add_hazard_zone(self, center: Tuple[float, float, float], 
                       radius: float, severity: float = 1.0):
        """Add a hazard zone to avoid"""
        self.hazard_zones.append((center, radius, severity))
        
    def clear_hazard_zones(self):
        """Clear all hazard zones"""
        self.hazard_zones = []
        self.route_cache.clear()
    
    def calculate_route_cost(self, start: Tuple[float, float, float],
                            end: Tuple[float, float, float]) -> float:
        """Calculate route cost considering hazards"""
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(start, end)))
        cost = distance
        
        # Check if path crosses hazard zones
        for center, radius, severity in self.hazard_zones:
            # Simplified: check if line passes near hazard
            d = self._distance_to_line(start, end, center)
            if d < radius:
                # Add cost based on proximity and severity
                hazard_cost = severity * (1 + (radius - d) / radius)
                cost *= (1 + hazard_cost)
        
        return cost
    
    def _distance_to_line(self, a: Tuple[float, float, float],
                         b: Tuple[float, float, float],
                         p: Tuple[float, float, float]) -> float:
        """Calculate distance from point p to line ab"""
        ab = [b[i] - a[i] for i in range(3)]
        ap = [p[i] - a[i] for i in range(3)]
        
        # Project p onto line
        t = sum(ab[i] * ap[i] for i in range(3)) / sum(ab[i] ** 2 for i in range(3))
        t = max(0, min(1, t))
        
        # Closest point on line
        closest = [a[i] + t * ab[i] for i in range(3)]
        
        # Distance to closest point
        return math.sqrt(sum((p[i] - closest[i]) ** 2 for i in range(3)))
    
    def optimize_route(self, start: Tuple[float, float, float],
                      end: Tuple[float, float, float],
                      waypoints: List[Tuple[float, float, float]] = None) -> Dict:
        """Optimize route with waypoints"""
        if waypoints is None:
            waypoints = []
        
        points = [start] + waypoints + [end]
        
        total_cost = 0
        route = [start]
        
        for i in range(len(points) - 1):
            cost = self.calculate_route_cost(points[i], points[i+1])
            total_cost += cost
            if i < len(waypoints):
                route.append(waypoints[i])
        
        route.append(end)
        
        return {
            'route': route,
            'total_cost': total_cost,
            'hazards_avoided': len(self.hazard_zones)
        }
    
    def get_safe_alternatives(self, position: Tuple[float, float, float],
                             radius: float) -> List[Tuple[float, float, float]]:
        """Get safe alternative positions within radius"""
        alternatives = []
        
        # Check 8 directions
        for dx in [-radius/2, 0, radius/2]:
            for dy in [-radius/2, 0, radius/2]:
                if dx == 0 and dy == 0:
                    continue
                
                alt = (position[0] + dx, position[1] + dy, position[2])
                
                # Check if safe from hazards
                safe = True
                for center, hazard_radius, severity in self.hazard_zones:
                    dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(alt, center)))
                    if dist < hazard_radius:
                        safe = False
                        break
                
                if safe:
                    alternatives.append(alt)
        
        return alternatives