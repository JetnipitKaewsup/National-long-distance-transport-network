"""
Drone model with battery management and mesh networking
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from enum import Enum
import heapq
import math

class DroneStatus(Enum):
    """Drone operational status"""
    IDLE = "idle"
    PATROLLING = "patrolling"
    CHARGING = "charging"
    DEPLOYING = "deploying"
    RETURNING = "returning"
    FAILED = "failed"

class DroneSpecs:
    """Drone specifications"""
    def __init__(self):
        self.battery_capacity = 3600  # Wh
        self.charge_rate = 600  # Wh per minute
        self.discharge_rate_patrol = 60  # Wh per minute
        self.discharge_rate_mesh = 90  # Wh per minute
        self.max_speed = 15  # m/s
        self.max_range = 1000  # meters
        self.mesh_range = 300  # meters

class Drone:
    """Individual drone with battery and communication"""
    
    def __init__(self, drone_id: str, position: Tuple[float, float, float]):
        self.id = drone_id
        self.position = position
        self.specs = DroneSpecs()
        self.battery_level = self.specs.battery_capacity
        self.status = DroneStatus.IDLE
        self.is_active = True
        self.connections = []
        self.mesh_routes = {}
        self.packets_forwarded = 0
        self.uptime = 0
        self.charge_cycles = 0
        self.target_position = None
        self.home_base = None
        
    def update_battery(self, dt: float, is_mesh_active: bool = False):
        """Update battery based on activity"""
        if self.status == DroneStatus.CHARGING:
            # Charging
            charge_amount = (self.specs.charge_rate / 60) * dt
            self.battery_level = min(
                self.specs.battery_capacity,
                self.battery_level + charge_amount
            )
            if self.battery_level >= self.specs.battery_capacity * 0.95:
                self.status = DroneStatus.IDLE
                self.is_active = True
        else:
            # Discharging
            if self.status == DroneStatus.PATROLLING:
                drain_rate = self.specs.discharge_rate_patrol / 60
            elif is_mesh_active:
                drain_rate = self.specs.discharge_rate_mesh / 60
            else:
                drain_rate = self.specs.discharge_rate_patrol / 60 * 0.5
            
            self.battery_level = max(0, self.battery_level - drain_rate * dt)
            
            if self.battery_level <= self.specs.battery_capacity * 0.1:
                self.is_active = False
                self.status = DroneStatus.RETURNING
                
        self.uptime += dt
    
    def can_reach(self, target: Tuple[float, float, float]) -> bool:
        """Check if drone can reach target"""
        distance = self._distance_to(target)
        energy_needed = (distance / self.specs.max_speed) * (self.specs.discharge_rate_patrol / 60)
        return self.battery_level > energy_needed * 1.2
    
    def _distance_to(self, target: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.position, target)))
    
    def move_towards(self, target: Tuple[float, float, float], dt: float):
        """Move towards target position"""
        if not self.is_active:
            return
            
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        dz = target[2] - self.position[2]
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        if distance < self.specs.max_speed * dt:
            self.position = target
            self.target_position = None
        else:
            ratio = (self.specs.max_speed * dt) / distance
            self.position = (
                self.position[0] + dx * ratio,
                self.position[1] + dy * ratio,
                self.position[2] + dz * ratio
            )
    
    def get_status(self) -> Dict:
        """Get drone status"""
        return {
            'id': self.id,
            'position': self.position,
            'battery': self.battery_level / self.specs.battery_capacity,
            'status': self.status.value,
            'active': self.is_active,
            'connections': len(self.connections),
            'packets_forwarded': self.packets_forwarded,
            'uptime': self.uptime,
            'charge_cycles': self.charge_cycles
        }

class DroneSwarm:
    """Manage multiple drones as a swarm"""
    def force_mesh_creation(self):
        """Force drones to create mesh network"""
        active_drones = [d_id for d_id, d in self.drones.items() if d.is_active]
        if len(active_drones) >= 2:
            self.create_mesh(active_drones)
            print(f"   📡 Created mesh with {len(active_drones)} drones")
    def __init__(self):
        self.drones: Dict[str, Drone] = {}
        self.charging_stations: List[Tuple[float, float, float]] = []
        self.mesh_network = {}
        
    def add_drone(self, drone: Drone):
        """Add drone to swarm"""
        self.drones[drone.id] = drone
        
    def add_charging_station(self, position: Tuple[float, float, float]):
        """Add charging station"""
        self.charging_stations.append(position)
        
    def deploy_swarm(self, target: Tuple[float, float, float], 
                    num_drones: int = 3) -> List[str]:
        """Deploy drones to target"""
        deployed = []
        
        # Find available drones
        available = [d for d in self.drones.values() 
                    if d.status == DroneStatus.IDLE and d.is_active]
        
        # Sort by battery and distance
        available.sort(key=lambda d: (
            -d.battery_level,
            d._distance_to(target)
        ))
        
        for drone in available[:num_drones]:
            if drone.can_reach(target):
                drone.status = DroneStatus.DEPLOYING
                drone.target_position = target
                deployed.append(drone.id)
                
        return deployed
    
    def create_mesh(self, drone_ids: List[str]) -> Dict[str, List[str]]:
        """Create mesh network between drones"""
        mesh = {}
        
        for i, d1_id in enumerate(drone_ids):
            if d1_id not in self.drones:
                continue
            d1 = self.drones[d1_id]
            mesh[d1_id] = []
            
            for j, d2_id in enumerate(drone_ids):
                if i == j or d2_id not in self.drones:
                    continue
                d2 = self.drones[d2_id]
                
                distance = d1._distance_to(d2.position)
                if distance < d1.specs.mesh_range:
                    mesh[d1_id].append(d2_id)
                    d1.connections.append(d2_id)
                    
        self.mesh_network = mesh
        return mesh
    
    def find_route(self, source: str, destination: str) -> Optional[List[str]]:
        """Find route through mesh using Dijkstra"""
        if source not in self.mesh_network or destination not in self.mesh_network:
            return None
            
        distances = {node: float('inf') for node in self.mesh_network}
        previous = {node: None for node in self.mesh_network}
        distances[source] = 0
        
        pq = [(0, source)]
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current == destination:
                break
                
            if current_dist > distances[current]:
                continue
                
            for neighbor in self.mesh_network[current]:
                distance = current_dist + 1
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        
        if distances[destination] == float('inf'):
            return None
        
        path = []
        current = destination
        while current:
            path.append(current)
            current = previous[current]
        
        return path[::-1]
    
    def calculate_coverage(self, drone_ids: List[str] = None) -> float:
        """Calculate coverage area in square meters"""
        if drone_ids is None:
            drone_ids = list(self.drones.keys())
            
        if not drone_ids:
            return 0
            
        covered_points = set()
        for d_id in drone_ids:
            if d_id not in self.drones:
                continue
            drone = self.drones[d_id]
            if not drone.is_active:
                continue
                
            x, y, _ = drone.position
            for dx in range(-250, 251, 50):
                for dy in range(-250, 251, 50):
                    if dx*dx + dy*dy <= 250*250:
                        covered_points.add((round(x + dx, -1), round(y + dy, -1)))
        
        return len(covered_points) * 2500
    
    def handle_low_battery(self, threshold: float = 0.2) -> List[Dict]:
        """Handle drones with low battery"""
        alerts = []
        
        for drone_id, drone in self.drones.items():
            battery_pct = drone.battery_level / drone.specs.battery_capacity
            
            if battery_pct < threshold and drone.status != DroneStatus.CHARGING:
                if drone.home_base and drone.can_reach(drone.home_base):
                    alerts.append({
                        'drone_id': drone_id,
                        'battery': battery_pct,
                        'action': 'return_to_base',
                        'target': drone.home_base
                    })
                else:
                    alerts.append({
                        'drone_id': drone_id,
                        'battery': battery_pct,
                        'action': 'emergency_land',
                        'target': drone.position
                    })
                    
        return alerts
    
    def hot_swap(self, patrol_id: str, backup_id: str) -> bool:
        """Swap patrol drone with backup"""
        if patrol_id not in self.drones or backup_id not in self.drones:
            return False
            
        patrol = self.drones[patrol_id]
        backup = self.drones[backup_id]
        
        if not backup.is_active or backup.battery_level < 0.8 * backup.specs.battery_capacity:
            return False
            
        # Transfer position and connections
        patrol_pos = patrol.position
        patrol_conns = patrol.connections.copy()
        
        backup.position = patrol_pos
        backup.connections = patrol_conns
        backup.status = DroneStatus.PATROLLING
        
        patrol.position = patrol.home_base if patrol.home_base else (0, 0, 0)
        patrol.connections = []
        patrol.status = DroneStatus.RETURNING
        patrol.charge_cycles += 1
        
        return True
    
    def update_all(self, dt: float):
        """Update all drones"""
        for drone in self.drones.values():
            if drone.target_position and drone.is_active:
                drone.move_towards(drone.target_position, dt)
                
                if drone.position == drone.target_position:
                    drone.status = DroneStatus.PATROLLING
                    drone.target_position = None
        
        active_drones = [d.id for d in self.drones.values() if d.is_active]
        if active_drones:
            self.create_mesh(active_drones)
    
    def get_swarm_status(self) -> Dict:
        """Get swarm status summary"""
        total = len(self.drones)
        active = sum(1 for d in self.drones.values() if d.is_active)
        
        # นับตาม status
        patrolling = sum(1 for d in self.drones.values() if d.status == DroneStatus.PATROLLING)
        charging = sum(1 for d in self.drones.values() if d.status == DroneStatus.CHARGING)
        deploying = sum(1 for d in self.drones.values() if d.status == DroneStatus.DEPLOYING)
        returning = sum(1 for d in self.drones.values() if d.status == DroneStatus.RETURNING)
        idle = sum(1 for d in self.drones.values() if d.status == DroneStatus.IDLE)
        failed = sum(1 for d in self.drones.values() if d.status == DroneStatus.FAILED)
        
        if active > 0:
            avg_battery = np.mean([d.battery_level / d.specs.battery_capacity 
                                for d in self.drones.values() if d.is_active])
        else:
            avg_battery = 0
        
        mesh_connections = sum(len(v) for v in self.mesh_network.values()) // 2
        
        return {
            'total': total,
            'active': active,
            'patrolling': patrolling,
            'charging': charging,
            'deploying': deploying,
            'returning': returning,
            'idle': idle,
            'failed': failed,
            'avg_battery': avg_battery,
            'coverage': self.calculate_coverage() / 1e6,
            'mesh_connections': mesh_connections
        }
    
    def hot_swap(self, patrol_id: str, backup_id: str) -> bool:
        """Swap patrol drone with backup"""
        if patrol_id not in self.drones or backup_id not in self.drones:
            return False
            
        patrol = self.drones[patrol_id]
        backup = self.drones[backup_id]
        
        if not backup.is_active or backup.battery_level < 0.8 * backup.specs.battery_capacity:
            return False
            
        # Transfer position and connections
        patrol_pos = patrol.position
        patrol_conns = patrol.connections.copy()
        
        backup.position = patrol_pos
        backup.connections = patrol_conns
        backup.status = DroneStatus.PATROLLING
        
        patrol.position = patrol.home_base if patrol.home_base else (0, 0, 0)
        patrol.connections = []
        patrol.status = DroneStatus.RETURNING
        patrol.charge_cycles += 1
        
        return True  # ต้องคืนค่า True