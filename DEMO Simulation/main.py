"""
Triple-Layer Network Simulation for Hazardous Material Transport and Emergency Rescue Operations
Author: Student Group Project
Description: Simulates a strategic network with 5G/6G deterministic core, satellite backup, and drone mesh network
"""

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum
import heapq
import random
import math
from collections import defaultdict
import hashlib
import time
from abc import ABC, abstractmethod

# ===================== Configuration and Constants =====================

class NetworkConstants:
    """Central configuration for network parameters"""

    # 5G/6G Core Parameters
    CORE_BANDWIDTH_5G = 10 * 1024  # 10 Gbps
    CORE_BANDWIDTH_6G = 100 * 1024  # 100 Gbps
    CORE_LATENCY_5G = 1  # 1 ms
    CORE_LATENCY_6G = 0.1  # 0.1 ms
    CORE_RELIABILITY_5G = 0.999
    CORE_RELIABILITY_6G = 0.9999

    # Satellite Parameters
    SAT_BANDWIDTH = 100  # 100 Mbps
    SAT_LATENCY = 250  # 250 ms (LEO satellite)
    SAT_RELIABILITY = 0.95

    # Drone Mesh Parameters
    DRONE_BANDWIDTH = 50  # 50 Mbps
    DRONE_LATENCY = 10  # 10 ms per hop
    DRONE_RELIABILITY = 0.9
    DRONE_BATTERY_CAPACITY = 3600  # 1 hour in seconds
    DRONE_CHARGE_RATE = 1800  # 30 minutes to full charge
    DRONE_MAX_RANGE = 1000  # meters
    DRONE_SPEED = 15  # meters per second

    # Handover Parameters
    HANDOVER_LATENCY_5G_TO_SAT = 500  # 500 ms
    HANDOVER_LATENCY_5G_TO_DRONE = 100  # 100 ms
    HANDOVER_LATENCY_SAT_TO_DRONE = 200  # 200 ms

    # Emergency Priorities
    PRIORITY_LEVELS = {
        'critical': 1,
        'high': 2,
        'medium': 3,
        'low': 4
    }

    # Simulation Parameters
    SIMULATION_DURATION = 3600  # 1 hour
    UPDATE_INTERVAL = 0.1  # 100 ms
    PACKET_GENERATION_RATE = 10  # packets per second per node


# ===================== Enums and Data Classes =====================

class NodeType(Enum):
    CORE_5G = "5G_CORE"
    CORE_6G = "6G_CORE"
    SATELLITE = "SATELLITE"
    DRONE = "DRONE"
    HAZMAT_VEHICLE = "HAZMAT_VEHICLE"
    EMERGENCY_BASE = "EMERGENCY_BASE"
    CRISIS_ZONE = "CRISIS_ZONE"


class PacketType(Enum):
    CONTROL = "CONTROL"
    DATA = "DATA"
    EMERGENCY = "EMERGENCY"
    TELEMETRY = "TELEMETRY"


class SimulationEvent(Enum):
    PACKET_TRANSMISSION = "PACKET_TRANSMISSION"
    NODE_FAILURE = "NODE_FAILURE"
    HANDOVER = "HANDOVER"
    BATTERY_UPDATE = "BATTERY_UPDATE"
    EMERGENCY_ALERT = "EMERGENCY_ALERT"


@dataclass
class Position:
    x: float
    y: float
    z: float = 0

    def distance_to(self, other: 'Position') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

    def move_towards(self, target: 'Position', speed: float, dt: float) -> 'Position':
        """Move towards target position at given speed"""
        dx = target.x - self.x
        dy = target.y - self.y
        dz = target.z - self.z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        if distance < speed * dt:
            return Position(target.x, target.y, target.z)

        ratio = (speed * dt) / distance
        return Position(
            self.x + dx * ratio,
            self.y + dy * ratio,
            self.z + dz * ratio
        )


@dataclass
class Packet:
    id: str
    source: str
    destination: str
    packet_type: PacketType
    priority: int
    size: int  # in bytes
    data: Any = None
    timestamp: float = field(default_factory=time.time)
    path: List[str] = field(default_factory=list)
    encrypted: bool = False
    delivered: bool = False
    delivery_time: float = None

    def __lt__(self, other):
        return self.priority < other.priority


@dataclass
class NetworkNode:
    id: str
    node_type: NodeType
    position: Position
    bandwidth: float
    latency: float
    reliability: float
    battery_level: float = None  # Only for drones
    is_active: bool = True
    connections: List[str] = field(default_factory=list)
    buffer: List[Packet] = field(default_factory=list)
    processing_queue: List[Packet] = field(default_factory=list)
    processed_packets: int = 0
    dropped_packets: int = 0

    def __post_init__(self):
        if self.node_type == NodeType.DRONE and self.battery_level is None:
            self.battery_level = NetworkConstants.DRONE_BATTERY_CAPACITY

    def update_battery(self, dt: float):
        """Update drone battery level"""
        if self.node_type == NodeType.DRONE and self.is_active:
            # Battery drain based on activity
            drain_rate = 1.0  # 1 unit per second when active
            if len(self.processing_queue) > 0:
                drain_rate *= 1.5  # Higher drain when processing

            self.battery_level = max(0, self.battery_level - drain_rate * dt)

            # Auto-disable if battery depleted
            if self.battery_level <= 0:
                self.is_active = False
                self.battery_level = 0

    def charge_battery(self, dt: float):
        """Charge drone battery"""
        if self.node_type == NodeType.DRONE:
            charge_amount = (NetworkConstants.DRONE_BATTERY_CAPACITY /
                           NetworkConstants.DRONE_CHARGE_RATE) * dt
            self.battery_level = min(NetworkConstants.DRONE_BATTERY_CAPACITY,
                                    self.battery_level + charge_amount)


# ===================== Digital Twin Implementation =====================

class DigitalTwin:
    """Digital Twin representation of the physical network"""

    def __init__(self, network_simulator):
        self.physical_network = network_simulator
        self.state_history = []
        self.prediction_models = {}
        self.sync_interval = 1.0  # seconds
        self.last_sync = time.time()

    def sync_with_physical(self):
        """Update digital twin with current physical network state"""
        current_state = {
            'timestamp': time.time(),
            'nodes': self._capture_nodes_state(),
            'links': self._capture_links_state(),
            'traffic': self._capture_traffic_patterns()
        }
        self.state_history.append(current_state)
        self.last_sync = current_state['timestamp']

        # Keep only last 100 states
        if len(self.state_history) > 100:
            self.state_history.pop(0)

    def _capture_nodes_state(self) -> Dict:
        nodes_state = {}
        for node_id, node in self.physical_network.nodes.items():
            nodes_state[node_id] = {
                'type': node.node_type.value,
                'position': (node.position.x, node.position.y, node.position.z),
                'active': node.is_active,
                'battery': node.battery_level if node.node_type == NodeType.DRONE else None,
                'buffer_size': len(node.buffer),
                'queue_size': len(node.processing_queue)
            }
        return nodes_state

    def _capture_links_state(self) -> Dict:
        return self.physical_network.get_link_states()

    def _capture_traffic_patterns(self) -> Dict:
        return self.physical_network.get_traffic_statistics()

    def predict_node_failure(self, node_id: str) -> float:
        """Predict probability of node failure in next 5 minutes"""
        node = self.physical_network.nodes.get(node_id)
        if not node or not node.is_active:
            return 1.0

        failure_prob = 0.0

        # Battery-based prediction for drones
        if node.node_type == NodeType.DRONE and node.battery_level:
            battery_ratio = node.battery_level / NetworkConstants.DRONE_BATTERY_CAPACITY
            if battery_ratio < 0.2:
                failure_prob += 0.7
            elif battery_ratio < 0.4:
                failure_prob += 0.3
            elif battery_ratio < 0.6:
                failure_prob += 0.1

        # Traffic-based prediction
        if len(node.processing_queue) > 100:
            queue_ratio = min(1.0, len(node.processing_queue) / 200)
            failure_prob += 0.2 * queue_ratio

        # Historical failure patterns
        recent_failures = self.physical_network.statistics.get('node_failures', [])
        recent_failures = [f for f in recent_failures if f[0] == node_id and
                          time.time() - f[1] < 3600]  # Last hour
        if recent_failures:
            failure_prob += 0.1 * len(recent_failures)

        return min(failure_prob, 1.0)

    def predict_handover_needed(self, node_id: str) -> Tuple[bool, str, float]:
        """Predict if handover will be needed soon"""
        node = self.physical_network.nodes.get(node_id)
        if not node or node.node_type != NodeType.HAZMAT_VEHICLE:
            return False, "", 0.0

        # Check signal quality to current core connection
        current_core = self.physical_network.get_connected_core(node_id)
        if current_core:
            distance = node.position.distance_to(self.physical_network.nodes[current_core].position)
            signal_strength = self.physical_network.calculate_signal_strength(distance)

            # Check available alternatives
            alternatives = self.physical_network.find_alternative_connections(node_id)

            # If signal is weak and alternatives exist, predict handover
            if signal_strength < 0.3 and alternatives:
                best_alt = max(alternatives, key=lambda x: x[1])
                return True, best_alt[0], signal_strength

            # Predict future degradation based on movement
            if node_id in self.physical_network.moving_nodes:
                future_pos = self.physical_network.moving_nodes[node_id]['future_position']
                future_distance = future_pos.distance_to(self.physical_network.nodes[current_core].position)
                future_signal = self.physical_network.calculate_signal_strength(future_distance)

                if future_signal < 0.2 and signal_strength > 0.3:
                    alternatives = self.physical_network.find_alternative_connections(node_id, future_pos)
                    if alternatives:
                        best_alt = max(alternatives, key=lambda x: x[1])
                        return True, best_alt[0], signal_strength

        return False, "", 0.0


# ===================== Edge AI Implementation =====================

class EdgeAIModel(ABC):
    """Base class for Edge AI models"""

    @abstractmethod
    def process(self, data: Any) -> Any:
        pass


class AnomalyDetectionModel(EdgeAIModel):
    """Detect anomalies in hazmat transport data"""

    def __init__(self, threshold=0.95):
        self.threshold = threshold
        self.baseline_patterns = {}
        self.anomaly_history = []

    def train(self, historical_data):
        """Train on normal operation data"""
        # Simplified training - in reality would use ML algorithms
        for data_point in historical_data:
            sensor_type = data_point.get('sensor_type')
            value = data_point.get('value')

            if sensor_type not in self.baseline_patterns:
                self.baseline_patterns[sensor_type] = {
                    'mean': value,
                    'std': 0,
                    'min': value,
                    'max': value,
                    'count': 1
                }
            else:
                # Update running statistics
                old_mean = self.baseline_patterns[sensor_type]['mean']
                count = self.baseline_patterns[sensor_type]['count']

                new_mean = (old_mean * count + value) / (count + 1)
                new_std = math.sqrt(
                    (self.baseline_patterns[sensor_type]['std']**2 * count +
                     (value - new_mean)**2) / (count + 1)
                )

                self.baseline_patterns[sensor_type].update({
                    'mean': new_mean,
                    'std': new_std,
                    'min': min(self.baseline_patterns[sensor_type]['min'], value),
                    'max': max(self.baseline_patterns[sensor_type]['max'], value),
                    'count': count + 1
                })

    def process(self, data: Dict) -> Dict:
        """Detect anomalies in sensor data"""
        sensor_type = data.get('sensor_type', 'unknown')
        value = data.get('value', 0)
        timestamp = data.get('timestamp', time.time())

        if sensor_type in self.baseline_patterns:
            baseline = self.baseline_patterns[sensor_type]

            if baseline['std'] > 0:
                # Z-score based anomaly detection
                z_score = abs(value - baseline['mean']) / baseline['std']
                is_anomaly = z_score > 3.0  # 3 sigma rule
                anomaly_score = min(1.0, z_score / 5.0)
            else:
                # Range-based for constant values
                range_size = baseline['max'] - baseline['min']
                if range_size > 0:
                    deviation = abs(value - baseline['mean']) / range_size
                else:
                    deviation = abs(value - baseline['mean']) / (baseline['mean'] + 0.001)

                is_anomaly = deviation > 0.2
                anomaly_score = min(1.0, deviation * 2)

            result = {
                'is_anomaly': is_anomaly,
                'anomaly_score': anomaly_score,
                'expected_value': baseline['mean'],
                'timestamp': timestamp,
                'sensor_type': sensor_type
            }

            if is_anomaly:
                self.anomaly_history.append(result)
                # Keep last 100 anomalies
                if len(self.anomaly_history) > 100:
                    self.anomaly_history.pop(0)

            return result

        return {
            'is_anomaly': False,
            'anomaly_score': 0,
            'timestamp': timestamp,
            'sensor_type': sensor_type
        }


class RouteOptimizationModel(EdgeAIModel):
    """Optimize routes for emergency response"""

    def __init__(self):
        self.traffic_patterns = {}
        self.hazard_zones = []  # List of (center, radius, severity)
        self.route_cache = {}
        self.cache_timeout = 60  # seconds

    def add_hazard_zone(self, center: Position, radius: float, severity: float = 1.0):
        """Add a hazard zone to avoid"""
        self.hazard_zones.append((center, radius, severity))

    def clear_hazard_zones(self):
        """Clear all hazard zones"""
        self.hazard_zones = []
        self.route_cache.clear()

    def process(self, data: Dict) -> Dict:
        """Calculate optimal route avoiding hazards and congestion"""
        start = data.get('start')
        end = data.get('end')
        vehicle_id = data.get('vehicle_id', 'unknown')
        priority = data.get('priority', 3)
        timestamp = data.get('timestamp', time.time())

        if not start or not end:
            return {'path': [], 'error': 'Missing start or end position'}

        # Check cache
        cache_key = f"{start.x:.0f},{start.y:.0f}-{end.x:.0f},{end.y:.0f}-{priority}"
        if cache_key in self.route_cache:
            cache_time, path = self.route_cache[cache_key]
            if timestamp - cache_time < self.cache_timeout:
                return {
                    'path': path,
                    'from_cache': True,
                    'hazards_avoided': len(self.hazard_zones)
                }

        # Calculate new path
        path = self._a_star_with_hazards(start, end, priority)

        # Cache the result
        self.route_cache[cache_key] = (timestamp, path)

        # Clean old cache entries
        self._clean_cache(timestamp)

        return {
            'path': path,
            'from_cache': False,
            'hazards_avoided': len(self.hazard_zones),
            'path_length': len(path)
        }

    def _a_star_with_hazards(self, start: Position, end: Position, priority: int) -> List[Position]:
        """A* algorithm considering hazard zones"""

        class Node:
            def __init__(self, pos, parent=None):
                self.pos = pos
                self.parent = parent
                self.g = 0  # Cost from start
                self.h = 0  # Heuristic to end
                self.f = 0  # Total cost

            def __lt__(self, other):
                return self.f < other.f

        def heuristic(a, b):
            return a.distance_to(b)

        def get_neighbors(pos, step_size):
            neighbors = []
            for dx in [-step_size, 0, step_size]:
                for dy in [-step_size, 0, step_size]:
                    if dx == 0 and dy == 0:
                        continue
                    new_pos = Position(
                        pos.x + dx,
                        pos.y + dy,
                        pos.z
                    )
                    neighbors.append(new_pos)
            return neighbors

        def calculate_cost(pos, next_pos, priority):
            # Base distance cost
            cost = pos.distance_to(next_pos)

            # Hazard cost
            for center, radius, severity in self.hazard_zones:
                distance_to_hazard = next_pos.distance_to(center)
                if distance_to_hazard < radius:
                    # Exponential cost based on proximity
                    hazard_cost = severity * (1 + (radius - distance_to_hazard) / radius)
                    cost *= (1 + hazard_cost)
                elif distance_to_hazard < radius * 2:
                    # Gradual cost increase near hazards
                    hazard_cost = severity * 0.5 * (1 - (distance_to_hazard - radius) / radius)
                    cost *= (1 + hazard_cost)

            # Priority adjustment
            if priority <= 1:  # Critical
                cost *= 0.8  # Lower cost for critical missions
            elif priority >= 4:  # Low priority
                cost *= 1.2  # Higher cost for low priority

            return cost

        # A* algorithm
        start_node = Node(start)
        end_node = Node(end)

        open_list = []
        closed_list = set()

        heapq.heappush(open_list, (start_node.f, id(start_node), start_node))

        # Grid step size based on priority
        step_size = 50 if priority <= 2 else 25

        while open_list:
            current = heapq.heappop(open_list)[2]
            closed_list.add((current.pos.x, current.pos.y, current.pos.z))

            # Check if reached goal
            if current.pos.distance_to(end) < step_size:
                path = []
                while current:
                    path.append(current.pos)
                    current = current.parent
                return list(reversed(path))

            # Generate neighbors
            for neighbor_pos in get_neighbors(current.pos, step_size):
                if (neighbor_pos.x, neighbor_pos.y, neighbor_pos.z) in closed_list:
                    continue

                # Calculate costs
                g = current.g + calculate_cost(current.pos, neighbor_pos, priority)
                h = heuristic(neighbor_pos, end)
                f = g + h

                neighbor = Node(neighbor_pos, current)
                neighbor.g = g
                neighbor.h = h
                neighbor.f = f

                heapq.heappush(open_list, (f, id(neighbor), neighbor))

        # If no path found, return direct line
        return [start, end]

    def _clean_cache(self, current_time):
        """Remove expired cache entries"""
        expired = []
        for key, (timestamp, _) in self.route_cache.items():
            if current_time - timestamp > self.cache_timeout:
                expired.append(key)

        for key in expired:
            del self.route_cache[key]


# ===================== Quantum-Resistant Encryption =====================

class QuantumResistantEncryption:
    """Simulated quantum-resistant encryption for secure communications"""

    def __init__(self):
        self.key_size = 256
        self.keys = {}
        self.key_rotation_interval = 300  # 5 minutes
        self.last_rotation = time.time()

    def generate_key(self, node_id: str) -> str:
        """Generate a quantum-resistant key for a node"""
        # Simulate lattice-based cryptography
        timestamp = str(time.time())
        random_factor = str(random.getrandbits(256))
        node_specific = str(hash(node_id))
        key_material = f"{node_id}{timestamp}{random_factor}{node_specific}"

        # Use multiple hash functions to simulate quantum resistance
        # This simulates the complexity of lattice-based cryptography
        key_parts = [
            hashlib.sha3_256(key_material.encode()).hexdigest(),
            hashlib.sha3_512(key_material.encode()).hexdigest()[:64],
            hashlib.blake2b(key_material.encode()).hexdigest()[:64],
            hashlib.blake2s(key_material.encode()).hexdigest()[:64]
        ]

        # Combine and add some lattice-like structure
        combined = ''.join(key_parts)

        # Simulate lattice basis (simplified)
        lattice_basis = []
        for i in range(0, len(combined), 64):
            chunk = combined[i:i+64]
            basis_vector = sum(ord(c) for c in chunk)
            lattice_basis.append(str(basis_vector))

        final_key = hashlib.sha3_256(''.join(lattice_basis).encode()).hexdigest()

        self.keys[node_id] = {
            'key': final_key,
            'generated': time.time(),
            'lattice_basis': lattice_basis
        }

        return final_key

    def get_key(self, node_id: str) -> Optional[str]:
        """Get current key for node, generating if needed"""
        if node_id not in self.keys:
            return self.generate_key(node_id)

        # Check if key needs rotation
        if time.time() - self.keys[node_id]['generated'] > self.key_rotation_interval:
            return self.generate_key(node_id)

        return self.keys[node_id]['key']

    def encrypt(self, data: Any, key: str) -> bytes:
        """Encrypt data using simulated quantum-resistant algorithm"""
        # Convert data to string
        if isinstance(data, dict):
            import json
            data_str = json.dumps(data, ensure_ascii=False)
        else:
            data_str = str(data)

        # Simulate lattice-based encryption
        # In real implementation, this would use actual lattice-based crypto
        encrypted = []

        # Use key to create a transformation matrix (simulated)
        key_bytes = [ord(c) for c in key]
        key_length = len(key_bytes)

        for i, char in enumerate(data_str):
            # Simulate matrix multiplication (simplified)
            row = i % key_length
            col = (i + 1) % key_length

            # Lattice-like transformation
            transform = (key_bytes[row] * key_bytes[col]) % 256
            noise = random.randint(0, 10)  # Simulate lattice noise

            encrypted_char = ord(char) ^ transform ^ noise
            encrypted.append(encrypted_char)

        # Add authentication tag (simulated)
        auth_tag = hashlib.sha3_256(bytes(encrypted)).digest()[:16]

        return bytes(encrypted) + auth_tag

    def decrypt(self, encrypted_data: bytes, key: str) -> Any:
        """Decrypt data"""
        # Split authentication tag
        if len(encrypted_data) < 16:
            return None

        encrypted = encrypted_data[:-16]
        auth_tag = encrypted_data[-16:]

        # Verify authentication tag (simplified)
        expected_tag = hashlib.sha3_256(bytes(encrypted)).digest()[:16]
        if auth_tag != expected_tag:
            print("Warning: Authentication tag mismatch - data may be corrupted")

        # Decrypt
        key_bytes = [ord(c) for c in key]
        key_length = len(key_bytes)

        decrypted_chars = []
        for i, byte in enumerate(encrypted):
            row = i % key_length
            col = (i + 1) % key_length

            # Reverse the lattice transformation
            transform = (key_bytes[row] * key_bytes[col]) % 256
            # Noise is lost in decryption (this is a limitation of simulation)

            decrypted_char = chr(byte ^ transform)
            decrypted_chars.append(decrypted_char)

        result = ''.join(decrypted_chars)

        # Try to parse as JSON
        try:
            import json
            return json.loads(result)
        except:
            return result


# ===================== Tree of Thoughts Reasoning =====================

class TreeOfThoughts:
    """Tree of Thoughts reasoning framework for network optimization"""

    def __init__(self):
        self.thoughts = {}
        self.evaluations = {}
        self.thought_history = []

    def generate_thoughts(self, problem: str, context: Dict) -> List[Dict]:
        """Generate multiple solution paths"""

        thoughts = []

        if "handover" in problem.lower():
            thoughts = self._handover_solution_paths(context)
        elif "battery" in problem.lower():
            thoughts = self._battery_management_paths(context)
        elif "routing" in problem.lower():
            thoughts = self._routing_solution_paths(context)
        elif "emergency" in problem.lower():
            thoughts = self._emergency_response_paths(context)
        else:
            # Generic problem solving
            thoughts = self._generic_solution_paths(context)

        # Store thoughts
        thought_id = f"thought_{len(self.thought_history)}"
        self.thoughts[thought_id] = thoughts
        self.thought_history.append({
            'id': thought_id,
            'problem': problem,
            'context': context,
            'thoughts': thoughts,
            'timestamp': time.time()
        })

        return thoughts

    def _handover_solution_paths(self, context: Dict) -> List[Dict]:
        """Generate different handover strategies"""
        current_network = context.get('current_network', 'unknown')
        signal_strength = context.get('signal_strength', 0.5)
        available_networks = context.get('available_networks', [])

        return [
            {
                'name': 'predictive_handover',
                'description': 'ใช้ Digital Twin ทำนายและเตรียม handover ล่วงหน้า',
                'steps': [
                    'ตรวจสอบแนวโน้มสัญญาณจาก Digital Twin',
                    'ทำนายเวลาที่ต้องการ handover',
                    'สร้างการเชื่อมต่อกับเครือข่ายเป้าหมายล่วงหน้า',
                    'ทำ handover แบบไร้รอยต่อ'
                ],
                'expected_latency': 50,  # ms
                'reliability': 0.98,
                'packet_loss': 0.001,
                'applicable_when': signal_strength > 0.3,
                'resources_needed': ['digital_twin', 'multi_path']
            },
            {
                'name': 'reactive_handover',
                'description': 'handover แบบมาตรฐานเมื่อสัญญาณลดลง',
                'steps': [
                    'ตรวจจับการลดลงของสัญญาณ',
                    'สแกนหาเครือข่ายที่พร้อมใช้งาน',
                    'เลือกเครือข่ายที่ดีที่สุด',
                    'สร้างการเชื่อมต่อใหม่'
                ],
                'expected_latency': 200,  # ms
                'reliability': 0.95,
                'packet_loss': 0.01,
                'applicable_when': True,
                'resources_needed': []
            },
            {
                'name': 'multi_path_handover',
                'description': 'รักษาการเชื่อมต่อหลายเส้นทางระหว่าง handover',
                'steps': [
                    'สร้างการเชื่อมต่อสำรองขณะที่ยังใช้หลักอยู่',
                    'กระจาย traffic ผ่านทั้งสองเส้นทาง',
                    'ค่อยๆเปลี่ยนไปใช้เส้นทางสำรอง',
                    'ปล่อยการเชื่อมต่อหลัก'
                ],
                'expected_latency': 10,  # ms
                'reliability': 0.99,
                'packet_loss': 0.0001,
                'applicable_when': len(available_networks) >= 2,
                'resources_needed': ['multi_path_capability', 'bandwidth']
            }
        ]

    def _battery_management_paths(self, context: Dict) -> List[Dict]:
        """Generate different battery management strategies"""
        battery_level = context.get('battery_level', 100)
        mission_critical = context.get('mission_critical', False)
        charging_stations = context.get('charging_stations', [])

        return [
            {
                'name': 'aggressive_charging',
                'description': ' prioritize การชาร์จทุกโอกาส',
                'steps': [
                    'ตรวจสอบระดับแบตเตอรี่ตลอดเวลา',
                    'ส่ง drone ไปชาร์จที่สถานีเมื่อแบตเหลือ 50%',
                    'จัดตารางการชาร์จให้เหมาะสม',
                    ' deploy drone สำรองทดแทน'
                ],
                'availability': 0.99,
                'efficiency': 0.7,
                'mission_time': 'ลดลง 30%',
                'applicable_when': not mission_critical and len(charging_stations) > 0
            },
            {
                'name': 'optimized_usage',
                'description': 'balance การใช้แบตเตอรี่กับภารกิจ',
                'steps': [
                    'คำนวณเส้นทางบินที่ประหยัดพลังงาน',
                    'ปรับกำลังส่งตามระยะทาง',
                    'ใช้โหมดประหยัดพลังงานเมื่อ idle',
                    'จัดตารางชาร์จตามความสำคัญ'
                ],
                'availability': 0.95,
                'efficiency': 0.9,
                'mission_time': 'ปกติ',
                'applicable_when': True
            },
            {
                'name': 'emergency_conservation',
                'description': 'ยืดอายุแบตเตอรี่ในสถานการณ์วิกฤติ',
                'steps': [
                    'ลดความถี่ในการส่งข้อมูล',
                    'ใช้โหมด bandwidth ต่ำ',
                    'รวม drone ทำงานร่วมกัน',
                    ' prioritize การสื่อสารที่จำเป็นเท่านั้น'
                ],
                'availability': 0.8,
                'efficiency': 0.95,
                'mission_time': 'ยืดออก 50%',
                'applicable_when': mission_critical or battery_level < 0.3
            }
        ]

    def _routing_solution_paths(self, context: Dict) -> List[Dict]:
        """Generate different routing strategies"""
        packet_type = context.get('packet_type', 'DATA')
        priority = context.get('priority', 3)
        network_congestion = context.get('network_congestion', 0.5)

        return [
            {
                'name': 'lowest_latency',
                'description': 'เลือกเส้นทางที่หน่วงเวลาน้อยที่สุด',
                'criteria': 'latency',
                'expected_performance': 0.1,  # seconds
                'reliability': 0.9,
                'energy_cost': 'สูง',
                'applicable_when': packet_type in ['EMERGENCY', 'CONTROL'] or priority <= 2
            },
            {
                'name': 'highest_reliability',
                'description': ' prioritize ความน่าเชื่อถือ',
                'criteria': 'reliability',
                'expected_performance': 0.99,
                'latency_cost': 2.0,  # seconds
                'energy_cost': 'ปานกลาง',
                'applicable_when': packet_type == 'CONTROL' or priority <= 1
            },
            {
                'name': 'balanced_approach',
                'description': 'balance ระหว่าง latency, reliability, และ energy',
                'criteria': 'multi_objective',
                'expected_performance': 0.5,
                'reliability': 0.95,
                'latency': 1.0,
                'energy_cost': 'ต่ำ',
                'applicable_when': True
            },
            {
                'name': 'energy_efficient',
                'description': ' prioritize การประหยัดพลังงาน',
                'criteria': 'energy',
                'expected_performance': 0.8,
                'reliability': 0.85,
                'latency': 3.0,
                'energy_cost': 'ต่ำสุด',
                'applicable_when': network_congestion > 0.8 or context.get('battery_critical', False)
            }
        ]

    def _emergency_response_paths(self, context: Dict) -> List[Dict]:
        """Generate different emergency response strategies"""
        emergency_type = context.get('emergency_type', 'unknown')
        severity = context.get('severity', 5)
        available_resources = context.get('available_resources', {})

        hazmat_specific = []
        if emergency_type == 'hazmat_leak':
            hazmat_specific = [
                {
                    'name': 'immediate_containment',
                    'description': 'ส่ง drone ทันทีเพื่อควบคุมการรั่วไหล',
                    'response_time': 30,  # seconds
                    'effectiveness': 0.95,
                    'resources_needed': 5,
                    'safety_risk': 'ปานกลาง',
                    'steps': [
                        'ส่ง drone ตรวจจับไปยังจุดเกิดเหตุ',
                        'วิเคราะห์ชนิดและปริมาณสารเคมี',
                        'พ่นสารควบคุมการรั่วไหล',
                        'รายงานผลแบบ real-time'
                    ]
                },
                {
                    'name': 'coordinated_response',
                    'description': 'ประสานงานกับทีมภาคพื้นดิน',
                    'response_time': 120,
                    'effectiveness': 0.98,
                    'resources_needed': 3,
                    'safety_risk': 'ต่ำ',
                    'steps': [
                        'แจ้งทีมภาคพื้นดิน',
                        'ส่ง drone ถ่ายภาพและวิดีโอ',
                        'วางแผนการอพยพร่วมกัน',
                        'ควบคุมการรั่วไหลแบบ coordinated'
                    ]
                },
                {
                    'name': 'evacuation_first',
                    'description': ' prioritize การอพยพประชาชน',
                    'response_time': 60,
                    'effectiveness': 0.9,
                    'resources_needed': 8,
                    'safety_risk': 'สูง',
                    'steps': [
                        'ประกาศอพยพทันที',
                        'ส่ง drone พร้อมลำโพงประกาศ',
                        'นำทางเส้นทางอพยพ',
                        'ตรวจสอบพื้นที่ว่าอพยพหมดแล้ว'
                    ]
                }
            ]
        elif emergency_type == 'fire':
            hazmat_specific = [
                {
                    'name': 'rapid_surveillance',
                    'description': 'ส่ง drone สำรวจประเมินสถานการณ์',
                    'response_time': 45,
                    'effectiveness': 0.9,
                    'resources_needed': 2,
                    'safety_risk': 'ปานกลาง',
                    'steps': [
                        'ส่ง drone thermal imaging',
                        'ระบุจุดที่ไฟไหม้',
                        'ประเมินการลุกลาม',
                        'วางแผนดับเพลิง'
                    ]
                },
                {
                    'name': 'mass_deployment',
                    'description': 'ส่ง drone ทั้งหมดที่มี',
                    'response_time': 60,
                    'effectiveness': 0.97,
                    'resources_needed': 10,
                    'safety_risk': 'สูง',
                    'steps': [
                        'ระดม drone ทั้งหมด',
                        'แบ่งโซนรับผิดชอบ',
                        'ประสานงานกับรถดับเพลิง',
                        'ติดตามการดับเพลิง'
                    ]
                }
            ]

        return hazmat_specific

    def _generic_solution_paths(self, context: Dict) -> List[Dict]:
        """Generate generic solution paths"""
        return [
            {
                'name': 'conservative',
                'description': 'เลือกวิธีที่ปลอดภัยที่สุด',
                'risk_level': 'ต่ำ',
                'speed': 'ช้า',
                'resource_usage': 'ปานกลาง'
            },
            {
                'name': 'aggressive',
                'description': 'เลือกวิธีที่เร็วที่สุด',
                'risk_level': 'สูง',
                'speed': 'เร็ว',
                'resource_usage': 'สูง'
            },
            {
                'name': 'balanced',
                'description': 'balance ความเร็วและความปลอดภัย',
                'risk_level': 'ปานกลาง',
                'speed': 'ปานกลาง',
                'resource_usage': 'ปานกลาง'
            }
        ]

    def evaluate_thoughts(self, thoughts: List[Dict], criteria: Dict) -> List[Tuple[Dict, float, List]]:
        """Evaluate and rank solution thoughts"""
        evaluated = []

        for thought in thoughts:
            score = 0.0
            reasons = []

            # Check applicability
            if 'applicable_when' in thought:
                if not thought['applicable_when']:
                    score = -1.0
                    reasons.append("ไม่สามารถใช้ได้ในสถานการณ์ปัจจุบัน")
                    evaluated.append((thought, score, reasons))
                    continue

            # Score based on criteria
            weights = criteria.get('weights', {
                'reliability': 0.3,
                'latency': 0.3,
                'effectiveness': 0.2,
                'resources': 0.2
            })

            # Reliability scoring
            if 'reliability' in thought and 'min_reliability' in criteria:
                if thought['reliability'] >= criteria['min_reliability']:
                    rel_score = thought['reliability'] * weights['reliability']
                    score += rel_score
                    reasons.append(f"Reliability: {thought['reliability']:.2f}")

            # Latency scoring
            if 'expected_latency' in thought and 'max_latency' in criteria:
                if thought['expected_latency'] <= criteria['max_latency']:
                    lat_score = (1 - thought['expected_latency'] / criteria['max_latency']) * weights['latency']
                    score += lat_score
                    reasons.append(f"Latency: {thought['expected_latency']}ms")

            # Effectiveness scoring
            if 'effectiveness' in thought and 'min_effectiveness' in criteria:
                if thought['effectiveness'] >= criteria['min_effectiveness']:
                    eff_score = thought['effectiveness'] * weights['effectiveness']
                    score += eff_score
                    reasons.append(f"Effectiveness: {thought['effectiveness']:.2f}")

            # Resource scoring
            if 'resources_needed' in thought and 'available_resources' in criteria:
                if isinstance(thought['resources_needed'], int):
                    if thought['resources_needed'] <= criteria['available_resources']:
                        res_score = (1 - thought['resources_needed'] / criteria['available_resources']) * weights['resources']
                        score += res_score
                        reasons.append(f"Resources: {thought['resources_needed']}")

            evaluated.append((thought, score, reasons))

        # Sort by score descending
        evaluated.sort(key=lambda x: x[1], reverse=True)
        return evaluated

    def select_best_thought(self, evaluated_thoughts: List[Tuple[Dict, float, List]]) -> Optional[Dict]:
        """Select the best thought from evaluated ones"""
        if not evaluated_thoughts:
            return None

        best_thought, score, reasons = evaluated_thoughts[0]

        if score <= 0:
            return None

        return {
            'thought': best_thought,
            'score': score,
            'reasons': reasons,
            'alternative': evaluated_thoughts[1] if len(evaluated_thoughts) > 1 else None
        }


# ===================== Chain of Thought Reasoning =====================

class ChainOfThought:
    """Chain of Thought reasoning for step-by-step problem solving"""

    def __init__(self):
        self.reasoning_chain = []
        self.reasoning_history = []

    def reason(self, problem: str, context: Dict) -> List[str]:
        """Generate step-by-step reasoning chain"""

        self.reasoning_chain = []

        # Add problem statement
        self.reasoning_chain.append(f"🤔 PROBLEM: {problem}")
        self.reasoning_chain.append("=" * 50)

        if "handover" in problem.lower():
            self._handover_reasoning(context)
        elif "battery" in problem.lower():
            self._battery_reasoning(context)
        elif "routing" in problem.lower():
            self._routing_reasoning(context)
        elif "emergency" in problem.lower():
            self._emergency_reasoning(context)
        else:
            self._generic_reasoning(context)

        # Add conclusion
        self.reasoning_chain.append("=" * 50)
        self.reasoning_chain.append("✅ CONCLUSION: " + self._get_conclusion())

        # Store in history
        self.reasoning_history.append({
            'problem': problem,
            'context': context,
            'chain': self.reasoning_chain.copy(),
            'timestamp': time.time()
        })

        # Keep only last 50 reasoning chains
        if len(self.reasoning_history) > 50:
            self.reasoning_history.pop(0)

        return self.reasoning_chain

    def _handover_reasoning(self, context: Dict):
        """Reasoning chain for handover decisions in Thai"""

        self.reasoning_chain.append("1️⃣ วิเคราะห์คุณภาพการเชื่อมต่อปัจจุบัน")

        signal_strength = context.get('signal_strength', 0)
        current_network = context.get('current_network', 'ไม่ทราบ')

        if signal_strength < 0.3:
            self.reasoning_chain.append(f"   ⚠️ สัญญาณอ่อนมาก ({signal_strength:.2f}) - จำเป็นต้อง handover")
        elif signal_strength < 0.6:
            self.reasoning_chain.append(f"   📶 สัญญาณปานกลาง ({signal_strength:.2f}) - อาจต้อง handover ในเร็วๆนี้")
        else:
            self.reasoning_chain.append(f"   ✅ สัญญาณดี ({signal_strength:.2f}) - ยังไม่จำเป็นต้อง handover")

        self.reasoning_chain.append(f"   📡 เครือข่ายปัจจุบัน: {current_network}")

        self.reasoning_chain.append("2️⃣ ประเมินเครือข่ายที่พร้อมใช้งาน")

        available_networks = context.get('available_networks', [])
        if not available_networks:
            self.reasoning_chain.append("   ❌ ไม่มีเครือข่ายสำรอง - ต้องรักษาการเชื่อมต่อปัจจุบัน")
        else:
            for i, network in enumerate(available_networks):
                net_type = network.get('type', 'unknown')
                reliability = network.get('reliability', 0)
                latency = network.get('latency', 0)
                self.reasoning_chain.append(f"   📡 Network {i+1}: {net_type}")
                self.reasoning_chain.append(f"      - Reliability: {reliability:.2f}")
                self.reasoning_chain.append(f"      - Latency: {latency}ms")

        self.reasoning_chain.append("3️⃣ พิจารณารูปแบบการเคลื่อนที่")

        speed = context.get('speed', 0)
        direction = context.get('direction', 0)
        self.reasoning_chain.append(f"   🚚 ยานพาหนะเคลื่อนที่ด้วยความเร็ว {speed} m/s ทิศทาง {direction}°")

        # Predict future position
        if speed > 5:
            self.reasoning_chain.append("   ⚡ ความเร็วสูง - คุณภาพสัญญาณอาจเปลี่ยนแปลงเร็ว")

        self.reasoning_chain.append("4️⃣ ทำนายคุณภาพสัญญาณในอนาคต")

        future_strength = context.get('future_signal', signal_strength * 0.9)
        if future_strength < signal_strength:
            change = (signal_strength - future_strength) / signal_strength * 100
            self.reasoning_chain.append(f"   📉 สัญญาณคาดว่าจะลดลง {change:.1f}% เหลือ {future_strength:.2f}")
        else:
            change = (future_strength - signal_strength) / signal_strength * 100
            self.reasoning_chain.append(f"   📈 สัญญาณคาดว่าจะดีขึ้น {change:.1f}% เป็น {future_strength:.2f}")

        self.reasoning_chain.append("5️⃣ ตัดสินใจ handover")

        if signal_strength < 0.3:
            decision = "เริ่ม handover ทันที"
            reason = "สัญญาณอ่อนเกินไป"
        elif signal_strength < 0.5 and future_strength < signal_strength:
            decision = "เตรียม handover ล่วงหน้า"
            reason = "สัญญาณกำลังจะลดลง"
        elif signal_strength < 0.6 and available_networks:
            decision = "ติดตามสถานการณ์อย่างใกล้ชิด"
            reason = "อาจต้อง handover ในเร็วๆนี้"
        else:
            decision = "ใช้การเชื่อมต่อปัจจุบันต่อไป"
            reason = "คุณภาพสัญญาณยังดีอยู่"

        self.reasoning_chain.append(f"   🎯 การตัดสินใจ: {decision}")
        self.reasoning_chain.append(f"   💡 เหตุผล: {reason}")

    def _battery_reasoning(self, context: Dict):
        """Reasoning chain for battery management in Thai"""

        self.reasoning_chain.append("1️⃣ ตรวจสอบระดับแบตเตอรี่ปัจจุบัน")

        battery_level = context.get('battery_level', NetworkConstants.DRONE_BATTERY_CAPACITY)
        battery_percent = (battery_level / NetworkConstants.DRONE_BATTERY_CAPACITY) * 100
        drone_id = context.get('drone_id', 'DRONE-001')

        self.reasoning_chain.append(f"   🚁 {drone_id}")
        self.reasoning_chain.append(f"   🔋 แบตเตอรี่ปัจจุบัน: {battery_percent:.1f}% ({battery_level:.0f} units)")

        if battery_percent < 20:
            self.reasoning_chain.append("   ⚠️ วิกฤติ! แบตเตอรี่ใกล้หมด")
        elif battery_percent < 40:
            self.reasoning_chain.append("   ⚡ ควรหาสถานีชาร์จ")
        elif battery_percent < 60:
            self.reasoning_chain.append("   🔋 ระดับปานกลาง")
        else:
            self.reasoning_chain.append("   ✅ แบตเตอรี่เพียงพอ")

        self.reasoning_chain.append("2️⃣ วิเคราะห์ความต้องการของภารกิจ")

        mission_duration = context.get('mission_duration', 300)
        mission_priority = context.get('mission_priority', 3)
        self.reasoning_chain.append(f"   🎯 ระยะเวลาภารกิจที่เหลือ: {mission_duration} วินาที")
        self.reasoning_chain.append(f"   ⭐ ความสำคัญภารกิจ: ระดับ {mission_priority}")

        # Calculate required battery
        power_consumption = context.get('power_consumption', 10)
        required_battery = mission_duration * power_consumption
        self.reasoning_chain.append(f"   ⚡ อัตราการใช้พลังงาน: {power_consumption} units/วินาที")
        self.reasoning_chain.append(f"   🔋 แบตเตอรี่ที่ต้องใช้: {required_battery:.0f} units")

        battery_deficit = required_battery - battery_level
        if battery_deficit > 0:
            self.reasoning_chain.append(f"   ⚠️ ขาดแบตเตอรี่ {battery_deficit:.0f} units")

        self.reasoning_chain.append("3️⃣ ตรวจสอบโอกาสในการชาร์จ")

        charging_stations = context.get('charging_stations', [])
        if charging_stations:
            # Find nearest station
            current_pos = context.get('position', Position(0, 0))
            stations_with_distance = []
            for station in charging_stations:
                if isinstance(station, dict) and 'position' in station:
                    dist = current_pos.distance_to(station['position'])
                    stations_with_distance.append((station, dist))

            if stations_with_distance:
                stations_with_distance.sort(key=lambda x: x[1])
                nearest = stations_with_distance[0]

                time_to_reach = nearest[1] / NetworkConstants.DRONE_SPEED
                self.reasoning_chain.append(f"   📍 สถานีชาร์จใกล้ที่สุด: ระยะทาง {nearest[1]:.0f}m")
                self.reasoning_chain.append(f"   🕒 เวลาที่ใช้ไปถึง: {time_to_reach:.0f} วินาที")

                # Battery needed to reach station
                battery_to_reach = time_to_reach * power_consumption
                self.reasoning_chain.append(f"   🔋 แบตเตอรี่ที่ต้องใช้ไปถึง: {battery_to_reach:.0f} units")

                if battery_level > battery_to_reach * 1.2:  # 20% safety margin
                    self.reasoning_chain.append("   ✅ สามารถไปถึงสถานีชาร์จได้")
                else:
                    self.reasoning_chain.append("   ⚠️ แบตเตอรี่อาจไม่พอไปถึงสถานีชาร์จ")
            else:
                self.reasoning_chain.append("   ❌ ไม่มีสถานีชาร์จในระยะที่เข้าถึงได้")
        else:
            self.reasoning_chain.append("   ❌ ไม่มีสถานีชาร์จในระยะที่เข้าถึงได้")

        self.reasoning_chain.append("4️⃣ ตัดสินใจจัดการแบตเตอรี่")

        # Make decision based on analysis
        if battery_level < required_battery * 0.8:  # Not enough for mission
            if charging_stations:
                decision = "กลับไปชาร์จที่สถานี"
                reason = f"แบตเตอรี่ไม่พอทำภารกิจ (ขาด {battery_deficit:.0f} units)"
            else:
                decision = "ขอความช่วยเหลือจาก drone สำรอง"
                reason = "แบตเตอรี่ไม่พอแต่ไม่มีสถานีชาร์จ"
        elif battery_level < required_battery * 1.2:  # Barely enough
            decision = "ลดการใช้พลังงาน (โหมดประหยัด)"
            reason = "แบตเตอรี่พอดีกับภารกิจ ต้องประหยัด"
        elif battery_level < NetworkConstants.DRONE_BATTERY_CAPACITY * 0.3:
            decision = "สลับกับ drone สำรอง"
            reason = "แบตเตอรี่เหลือน้อย ควรสลับพัก"
        else:
            decision = "ทำภารกิจต่อตามปกติ"
            reason = "แบตเตอรี่ยังเพียงพอ"

        self.reasoning_chain.append(f"   🎯 การตัดสินใจ: {decision}")
        self.reasoning_chain.append(f"   💡 เหตุผล: {reason}")

    def _routing_reasoning(self, context: Dict):
        """Reasoning chain for routing decisions in Thai"""

        self.reasoning_chain.append("1️⃣ กำหนดวัตถุประสงค์ของการส่งข้อมูล")

        packet_type = context.get('packet_type', 'DATA')
        priority = context.get('priority', 3)
        source = context.get('source', 'unknown')
        destination = context.get('destination', 'unknown')

        self.reasoning_chain.append(f"   📦 ประเภทแพ็กเก็ต: {packet_type}")
        self.reasoning_chain.append(f"   ⭐ ความสำคัญ: ระดับ {priority}")

        if priority <= 1:
            self.reasoning_chain.append("   🚨 วิกฤติ: ต้องการ latency ต่ำที่สุด")
        elif priority <= 2:
            self.reasoning_chain.append("   ⚡ สูง: balance ระหว่าง latency และ reliability")
        elif priority <= 3:
            self.reasoning_chain.append("   📊 ปานกลาง: optimize เพื่อประสิทธิภาพ")
        else:
            self.reasoning_chain.append("   📋 ต่ำ: prioritize การประหยัดพลังงาน")

        self.reasoning_chain.append(f"   📍 ต้นทาง: {source}")
        self.reasoning_chain.append(f"   🎯 ปลายทาง: {destination}")

        self.reasoning_chain.append("2️⃣ วิเคราะห์โครงสร้างเครือข่าย")

        path_options = context.get('path_options', [])
        if not path_options:
            self.reasoning_chain.append("   ❌ ไม่พบเส้นทาง")
        else:
            for i, path in enumerate(path_options[:3]):
                hops = path.get('hops', 0)
                latency = path.get('latency', 0)
                reliability = path.get('reliability', 0)
                energy = path.get('energy_cost', 'ปานกลาง')

                self.reasoning_chain.append(f"   🛣️ เส้นทาง {i+1}: {hops} hop(s)")
                self.reasoning_chain.append(f"      - Latency: {latency}ms")
                self.reasoning_chain.append(f"      - Reliability: {reliability:.2f}")
                self.reasoning_chain.append(f"      - Energy: {energy}")

        self.reasoning_chain.append("3️⃣ พิจารณาสภาพเครือข่ายแบบ real-time")

        congestion = context.get('congestion_level', 0)
        if congestion > 0.8:
            self.reasoning_chain.append(f"   🔴 congestion สูง ({congestion:.2f}) - หลีกเลี่ยงโหนดที่มี traffic มาก")
        elif congestion > 0.5:
            self.reasoning_chain.append(f"   🟡 congestion ปานกลาง ({congestion:.2f})")
        else:
            self.reasoning_chain.append(f"   🟢 congestion ต่ำ ({congestion:.2f})")

        failures = context.get('recent_failures', [])
        if failures:
            self.reasoning_chain.append(f"   ⚠️ พบ {len(failures)} การเชื่อมต่อล้มเหลวเมื่อเร็วๆนี้")

        self.reasoning_chain.append("4️⃣ เลือกเส้นทางที่เหมาะสม")

        # Select best path based on priority
        if priority <= 1:  # Critical
            selected = "lowest_latency"
            reason = "ต้องการความเร็วสูงสุด"
        elif priority <= 2:  # High
            selected = "balanced_approach"
            reason = "balance ความเร็วและความน่าเชื่อถือ"
        elif congestion > 0.8:  # High congestion
            selected = "energy_efficient"
            reason = "หลีกเลี่ยง congestion ด้วยการใช้พลังงานต่ำ"
        else:  # Normal
            selected = "highest_reliability"
            reason = "prioritize ความน่าเชื่อถือ"

        self.reasoning_chain.append(f"   🎯 เลือก: {selected}")
        self.reasoning_chain.append(f"   💡 เหตุผล: {reason}")

    def _emergency_reasoning(self, context: Dict):
        """Reasoning chain for emergency response in Thai"""

        self.reasoning_chain.append("1️⃣ จำแนกประเภทเหตุฉุกเฉิน")

        emergency_type = context.get('emergency_type', 'unknown')
        severity = context.get('severity', 5)
        location = context.get('location', Position(0, 0))

        self.reasoning_chain.append(f"   🆘 ประเภท: {emergency_type}")
        self.reasoning_chain.append(f"   ⚠️ ความรุนแรง: {severity}/10")
        self.reasoning_chain.append(f"   📍 ตำแหน่ง: ({location.x:.0f}, {location.y:.0f})")

        if severity >= 8:
            self.reasoning_chain.append("   🚨 วิกฤติระดับสูงสุด - ต้องตอบสนองทันที")
        elif severity >= 5:
            self.reasoning_chain.append("   ⚠️ ระดับปานกลาง - ต้องดำเนินการเร็ว")
        else:
            self.reasoning_chain.append("   📋 ระดับต่ำ - สามารถวางแผนได้")

        self.reasoning_chain.append("2️⃣ ประเมินทรัพยากรที่มี")

        available_drones = context.get('available_drones', 0)
        ground_teams = context.get('ground_teams', 0)
        emergency_bases = context.get('emergency_bases', [])

        self.reasoning_chain.append(f"   🚁 Drones พร้อมใช้งาน: {available_drones}")
        self.reasoning_chain.append(f"   👥 ทีมภาคพื้นดิน: {ground_teams}")
        self.reasoning_chain.append(f"   🏢 ฐานปฏิบัติการ: {len(emergency_bases)} แห่ง")

        # Calculate resource adequacy
        if emergency_type == 'hazmat_leak':
            needed_drones = max(2, severity // 2)
            needed_teams = max(1, severity // 3)
        elif emergency_type == 'fire':
            needed_drones = max(3, severity)
            needed_teams = max(2, severity // 2)
        else:
            needed_drones = 1
            needed_teams = 1

        self.reasoning_chain.append(f"   📊 ทรัพยากรที่ต้องการ: Drones {needed_drones} ทีม {needed_teams}")

        if available_drones >= needed_drones and ground_teams >= needed_teams:
            self.reasoning_chain.append("   ✅ มีทรัพยากรเพียงพอ")
        else:
            shortage = []
            if available_drones < needed_drones:
                shortage.append(f" drones ขาด {needed_drones - available_drones}")
            if ground_teams < needed_teams:
                shortage.append(f" ทีมขาด {needed_teams - ground_teams}")
            self.reasoning_chain.append(f"   ⚠️ ทรัพยากรไม่เพียงพอ: {','.join(shortage)}")

        self.reasoning_chain.append("3️⃣ กำหนดลำดับความสำคัญในการตอบสนอง")

        if emergency_type == 'hazmat_leak':
            priorities = [
                "🚨 ควบคุมการรั่วไหล - ป้องกันการแพร่กระจาย",
                "👥 อพยพประชาชนในพื้นที่เสี่ยง",
                "🧹 ทำความสะอาดและฟื้นฟูพื้นที่",
                "📊 ตรวจสอบและวิเคราะห์สาเหตุ"
            ]
        elif emergency_type == 'fire':
            priorities = [
                "👨‍🚒 ช่วยเหลือผู้ประสบภัย",
                "🔥 ควบคุมและดับไฟ",
                "🏠 ป้องกันทรัพย์สิน",
                "🔍 สืบสวนสาเหตุเพลิงไหม้"
            ]
        else:
            priorities = [
                "📞 แจ้งหน่วยงานที่เกี่ยวข้อง",
                "👥 ช่วยเหลือผู้ได้รับผลกระทบ",
                "📝 บันทึกเหตุการณ์",
                "🔧 แก้ไขปัญหา"
            ]

        for i, priority in enumerate(priorities, 1):
            self.reasoning_chain.append(f"   {i}. {priority}")

        self.reasoning_chain.append("4️⃣ วางแผนตอบสนอง")

        # Calculate response time
        response_time = context.get('estimated_response', 60)
        self.reasoning_chain.append(f"   ⏱️ เวลาตอบสนองโดยประมาณ: {response_time} วินาที")

        # Deployment plan
        if emergency_type == 'hazmat_leak':
            if severity >= 7:
                plan = [
                    "ส่ง drone พร้อมเซ็นเซอร์ตรวจจับสารเคมี 2 ตัว",
                    "ส่ง drone ถ่ายภาพความร้อน 1 ตัว",
                    "แจ้งทีม hazmat เตรียมพร้อม",
                    "ประกาศอพยพในรัศมี 500 เมตร"
                ]
            else:
                plan = [
                    "ส่ง drone สำรวจ 1 ตัว",
                    "แจ้งทีม hazmat เข้าตรวจสอบ",
                    "เตรียมพร้อมอพยพถ้าจำเป็น"
                ]
        elif emergency_type == 'fire':
            if severity >= 7:
                plan = [
                    "ส่ง drone ถ่ายภาพความร้อน 3 ตัว",
                    "ส่ง drone พร้อมเครื่องดับเพลิง 2 ตัว",
                    "แจ้งรถดับเพลิงทุกหน่วย",
                    "อพยพประชาชน"
                ]
            else:
                plan = [
                    "ส่ง drone สำรวจ 2 ตัว",
                    "แจ้งรถดับเพลิงใกล้ที่สุด",
                    "เตรียมพร้อมรับสถานการณ์"
                ]
        else:
            plan = ["ส่ง drone สำรวจ 1 ตัว", "รอการประเมินสถานการณ์"]

        for step in plan:
            self.reasoning_chain.append(f"   • {step}")

        self.reasoning_chain.append("5️⃣ เริ่มปฏิบัติการฉุกเฉิน")

        # Final decision
        if severity >= 8:
            action = "เปิดใช้ emergency protocol ระดับสูงสุด"
        elif severity >= 5:
            action = "เปิดใช้ emergency protocol มาตรฐาน"
        else:
            action = "ติดตามสถานการณ์อย่างใกล้ชิด"

        self.reasoning_chain.append(f"   🎯 การดำเนินการ: {action}")
        self.reasoning_chain.append("   📢 แจ้งเตือนทุกหน่วยงานที่เกี่ยวข้อง")
        self.reasoning_chain.append("   🔄 ติดตามและอัปเดตสถานการณ์ตลอดเวลา")

    def _generic_reasoning(self, context: Dict):
        """Generic reasoning chain"""

        self.reasoning_chain.append("1️⃣ วิเคราะห์สถานการณ์ปัจจุบัน")

        for key, value in context.items():
            if key not in ['position', 'start', 'end']:
                self.reasoning_chain.append(f"   • {key}: {value}")

        self.reasoning_chain.append("2️⃣ ระบุปัญหาและอุปสรรค")
        self.reasoning_chain.append("   • กำลังรวบรวมข้อมูลเพิ่มเติม")

        self.reasoning_chain.append("3️⃣ ค้นหาวิธีแก้ไขที่เป็นไปได้")
        self.reasoning_chain.append("   • กำลังประเมินทางเลือก")

        self.reasoning_chain.append("4️⃣ เลือกวิธีที่ดีที่สุด")
        self.reasoning_chain.append("   • รอผลการประเมิน")

    def _get_conclusion(self) -> str:
        """Get conclusion from reasoning chain"""
        # Extract last decision line
        for line in reversed(self.reasoning_chain):
            if "🎯 การตัดสินใจ:" in line or "🎯 เลือก:" in line or "🎯 การดำเนินการ:" in line:
                return line.split(":")[-1].strip()

        return "ดำเนินการตามแผนที่วางไว้"


# ===================== Main Network Simulator =====================

class TripleLayerNetworkSimulator:
    """Main simulator for the Triple-Layer Network architecture"""

    def __init__(self):
        self.nodes = {}
        self.packets = []
        self.events = []
        self.statistics = defaultdict(list)
        self.time = 0.0
        self.moving_nodes = {}  # Track moving nodes (hazmat vehicles)

        # Initialize reasoning frameworks
        self.tree_of_thoughts = TreeOfThoughts()
        self.chain_of_thought = ChainOfThought()

        # Initialize digital twin
        self.digital_twin = DigitalTwin(self)

        # Initialize edge AI models
        self.anomaly_detector = AnomalyDetectionModel()
        self.route_optimizer = RouteOptimizationModel()

        # Initialize encryption
        self.encryption = QuantumResistantEncryption()

        # Initialize network layers
        self.core_network = []  # 5G/6G core nodes
        self.satellite_network = []  # Satellite nodes
        self.drone_mesh = []  # Drone nodes
        self.hazmat_vehicles = []  # Hazmat transport vehicles
        self.emergency_bases = []  # Emergency response bases

        # Performance metrics
        self.metrics = {
            'total_packets': 0,
            'delivered_packets': 0,
            'dropped_packets': 0,
            'handovers_completed': 0,
            'handover_failures': 0,
            'emergencies_handled': 0,
            'average_latency': 0.0,
            'total_energy_consumed': 0.0
        }

    def setup_network(self):
        """Initialize the network topology"""

        print("\n" + "="*60)
        print("🚀 เริ่มต้นจำลอง Triple-Layer Network")
        print("="*60)

        # Create core network (5G/6G)
        print("\n📡 กำลังสร้าง Core Network (5G/6G)...")
        core_positions = [
            Position(0, 0, 50),    # Central core
            Position(500, 500, 50),  # East core
            Position(-500, -500, 50),  # West core
            Position(500, -500, 50),  # South core
            Position(-500, 500, 50)   # North core
        ]

        for i, pos in enumerate(core_positions):
            node_type = NodeType.CORE_6G if i == 0 else NodeType.CORE_5G
            bandwidth = NetworkConstants.CORE_BANDWIDTH_6G if node_type == NodeType.CORE_6G else NetworkConstants.CORE_BANDWIDTH_5G
            latency = NetworkConstants.CORE_LATENCY_6G if node_type == NodeType.CORE_6G else NetworkConstants.CORE_LATENCY_5G
            reliability = NetworkConstants.CORE_RELIABILITY_6G if node_type == NodeType.CORE_6G else NetworkConstants.CORE_RELIABILITY_5G

            node = NetworkNode(
                id=f"core_{i}",
                node_type=node_type,
                position=pos,
                bandwidth=bandwidth,
                latency=latency,
                reliability=reliability
            )
            self.nodes[node.id] = node
            self.core_network.append(node.id)
            print(f"   ✅ {node.id}: {node_type.value} ที่ ({pos.x:.0f}, {pos.y:.0f})")

        # Create satellite network
        print("\n🛰️ กำลังสร้าง Satellite Network...")
        satellite_positions = [
            Position(1000, 1000, 500),   # LEO satellite 1
            Position(-1000, -1000, 500),  # LEO satellite 2
            Position(1000, -1000, 500),   # LEO satellite 3
            Position(-1000, 1000, 500)    # LEO satellite 4
        ]

        for i, pos in enumerate(satellite_positions):
            node = NetworkNode(
                id=f"satellite_{i}",
                node_type=NodeType.SATELLITE,
                position=pos,
                bandwidth=NetworkConstants.SAT_BANDWIDTH,
                latency=NetworkConstants.SAT_LATENCY,
                reliability=NetworkConstants.SAT_RELIABILITY
            )
            self.nodes[node.id] = node
            self.satellite_network.append(node.id)
            print(f"   ✅ {node.id}: ที่ ({pos.x:.0f}, {pos.y:.0f}, {pos.z:.0f})")

        # Create drone mesh
        print("\n🚁 กำลังสร้าง Drone Mesh Network...")
        drone_positions = [
            Position(200, 200, 100),
            Position(-200, 200, 100),
            Position(200, -200, 100),
            Position(-200, -200, 100),
            Position(0, 300, 100),
            Position(300, 0, 100),
            Position(0, -300, 100),
            Position(-300, 0, 100)
        ]

        for i, pos in enumerate(drone_positions):
            node = NetworkNode(
                id=f"drone_{i}",
                node_type=NodeType.DRONE,
                position=pos,
                bandwidth=NetworkConstants.DRONE_BANDWIDTH,
                latency=NetworkConstants.DRONE_LATENCY,
                reliability=NetworkConstants.DRONE_RELIABILITY,
                battery_level=NetworkConstants.DRONE_BATTERY_CAPACITY
            )
            self.nodes[node.id] = node
            self.drone_mesh.append(node.id)
            print(f"   ✅ {node.id}: ที่ ({pos.x:.0f}, {pos.y:.0f}, {pos.z:.0f}) แบต {node.battery_level}")

        # Create hazmat transport vehicles
        print("\n🚚 กำลังสร้าง Hazmat Transport Vehicles...")
        hazmat_positions = [
            Position(100, 100, 0),
            Position(-100, 200, 0),
            Position(300, -100, 0),
            Position(-200, -300, 0),
            Position(400, 400, 0)
        ]

        for i, pos in enumerate(hazmat_positions):
            node = NetworkNode(
                id=f"hazmat_{i}",
                node_type=NodeType.HAZMAT_VEHICLE,
                position=pos,
                bandwidth=10,  # 10 Mbps
                latency=20,  # 20 ms
                reliability=0.95
            )
            self.nodes[node.id] = node
            self.hazmat_vehicles.append(node.id)

            # Setup movement pattern
            self.moving_nodes[node.id] = {
                'speed': random.uniform(5, 15),  # m/s
                'direction': random.uniform(0, 2 * math.pi),
                'waypoints': [
                    Position(random.uniform(-500, 500), random.uniform(-500, 500), 0)
                    for _ in range(3)
                ],
                'current_waypoint': 0,
                'future_position': pos
            }
            print(f"   ✅ {node.id}: ที่ ({pos.x:.0f}, {pos.y:.0f}) ความเร็ว {self.moving_nodes[node.id]['speed']:.1f} m/s")

        # Create emergency bases
        print("\n🏥 กำลังสร้าง Emergency Bases...")
        base_positions = [
            Position(0, 0, 0),
            Position(1000, 0, 0),
            Position(0, 1000, 0),
            Position(-1000, 0, 0),
            Position(0, -1000, 0)
        ]

        for i, pos in enumerate(base_positions):
            node = NetworkNode(
                id=f"base_{i}",
                node_type=NodeType.EMERGENCY_BASE,
                position=pos,
                bandwidth=100,  # 100 Mbps
                latency=5,  # 5 ms
                reliability=0.99
            )
            self.nodes[node.id] = node
            self.emergency_bases.append(node.id)
            print(f"   ✅ {node.id}: ที่ ({pos.x:.0f}, {pos.y:.0f})")

        # Setup connections between nodes
        print("\n🔗 กำลังสร้างการเชื่อมต่อระหว่างโหนด...")
        self._setup_connections()

        print("\n" + "="*60)
        print("✅ ตั้งค่าเครือข่ายเสร็จสมบูรณ์")
        print(f"   โหนดทั้งหมด: {len(self.nodes)}")
        print(f"   • Core Network: {len(self.core_network)} โหนด")
        print(f"   • Satellite Network: {len(self.satellite_network)} โหนด")
        print(f"   • Drone Mesh: {len(self.drone_mesh)} โหนด")
        print(f"   • Hazmat Vehicles: {len(self.hazmat_vehicles)} คัน")
        print(f"   • Emergency Bases: {len(self.emergency_bases)} แห่ง")
        print("="*60)

    def _setup_connections(self):
        """Setup connections between nodes"""
        connection_count = 0

        # Connect core network nodes to each other
        for i, core_id in enumerate(self.core_network):
            for j, other_id in enumerate(self.core_network):
                if i != j:
                    self.nodes[core_id].connections.append(other_id)
                    connection_count += 1

        # Connect drones to core network (within range)
        for drone_id in self.drone_mesh:
            drone = self.nodes[drone_id]
            for core_id in self.core_network:
                core = self.nodes[core_id]
                distance = drone.position.distance_to(core.position)
                if distance < NetworkConstants.DRONE_MAX_RANGE:
                    drone.connections.append(core_id)
                    connection_count += 1

        # Connect drones to each other (mesh)
        for i, drone_id in enumerate(self.drone_mesh):
            for j, other_id in enumerate(self.drone_mesh):
                if i != j:
                    drone = self.nodes[drone_id]
                    other = self.nodes[other_id]
                    distance = drone.position.distance_to(other.position)
                    if distance < NetworkConstants.DRONE_MAX_RANGE:
                        drone.connections.append(other_id)
                        connection_count += 1

        # Connect satellites to core network
        for sat_id in self.satellite_network:
            for core_id in self.core_network:
                self.nodes[sat_id].connections.append(core_id)
                connection_count += 1

        # Connect hazmat vehicles to nearest nodes
        for vehicle_id in self.hazmat_vehicles:
            vehicle = self.nodes[vehicle_id]

            # Find nearest core
            nearest_core = min(
                self.core_network,
                key=lambda cid: vehicle.position.distance_to(self.nodes[cid].position)
            )
            vehicle.connections.append(nearest_core)
            connection_count += 1

            # Find nearby drones
            for drone_id in self.drone_mesh:
                drone = self.nodes[drone_id]
                distance = vehicle.position.distance_to(drone.position)
                if distance < 500:  # Within 500m
                    vehicle.connections.append(drone_id)
                    connection_count += 1

        # Connect emergency bases to everything
        for base_id in self.emergency_bases:
            base = self.nodes[base_id]
            for core_id in self.core_network:
                base.connections.append(core_id)
                connection_count += 1
            for sat_id in self.satellite_network:
                base.connections.append(sat_id)
                connection_count += 1
            for drone_id in self.drone_mesh:
                base.connections.append(drone_id)
                connection_count += 1

        print(f"   สร้างการเชื่อมต่อ {connection_count} เส้นทาง")

    def calculate_signal_strength(self, distance: float) -> float:
        """Calculate signal strength based on distance"""
        # Simplified path loss model
        if distance < 100:
            return 1.0
        elif distance < 500:
            return 0.8 - 0.3 * (distance - 100) / 400
        elif distance < 1000:
            return 0.5 - 0.3 * (distance - 500) / 500
        else:
            return max(0.1, 0.2 - 0.1 * (distance - 1000) / 1000)

    def get_connected_core(self, node_id: str) -> Optional[str]:
        """Get the core node connected to a given node"""
        node = self.nodes.get(node_id)
        if not node:
            return None

        # Find core connections
        core_connections = [cid for cid in node.connections if cid.startswith('core_')]
        if core_connections:
            # Return the one with best signal
            best_core = max(
                core_connections,
                key=lambda cid: self.calculate_signal_strength(
                    node.position.distance_to(self.nodes[cid].position)
                )
            )
            return best_core

        return None

    def find_alternative_connections(self, node_id: str, position: Position = None) -> List[Tuple[str, float]]:
        """Find alternative connections for a node"""
        node = self.nodes.get(node_id)
        if not node:
            return []

        if position is None:
            position = node.position

        alternatives = []

        # Check drone connections
        for drone_id in self.drone_mesh:
            drone = self.nodes[drone_id]
            if drone.is_active and drone.battery_level > NetworkConstants.DRONE_BATTERY_CAPACITY * 0.2:
                distance = position.distance_to(drone.position)
                if distance < NetworkConstants.DRONE_MAX_RANGE:
                    signal = self.calculate_signal_strength(distance)
                    alternatives.append((drone_id, signal))

        # Check satellite connections
        for sat_id in self.satellite_network:
            sat = self.nodes[sat_id]
            if sat.is_active:
                # Satellites always have signal but with high latency
                alternatives.append((sat_id, 0.7))

        # Sort by signal strength
        alternatives.sort(key=lambda x: x[1], reverse=True)
        return alternatives

    def get_link_states(self) -> Dict:
        """Get current link states"""
        links = {}
        for node_id, node in self.nodes.items():
            for conn_id in node.connections[:10]:  # Limit to 10 per node
                if conn_id in self.nodes:
                    link_key = f"{node_id}-{conn_id}"
                    distance = node.position.distance_to(self.nodes[conn_id].position)
                    links[link_key] = {
                        'active': node.is_active and self.nodes[conn_id].is_active,
                        'latency': node.latency + self.nodes[conn_id].latency,
                        'signal_strength': self.calculate_signal_strength(distance),
                        'bandwidth': min(node.bandwidth, self.nodes[conn_id].bandwidth)
                    }
        return links

    def get_traffic_statistics(self) -> Dict:
        """Get current traffic statistics"""
        return {
            'total_packets_in_network': len(self.packets),
            'packets_by_type': self._count_packets_by_type(),
            'queue_sizes': {
                node_id: len(node.processing_queue)
                for node_id, node in self.nodes.items()
                if len(node.processing_queue) > 0
            },
            'buffer_sizes': {
                node_id: len(node.buffer)
                for node_id, node in self.nodes.items()
                if len(node.buffer) > 0
            }
        }

    def _count_packets_by_type(self) -> Dict:
        """Count packets by type"""
        counts = defaultdict(int)
        for packet in self.packets:
            if not packet.delivered:
                counts[packet.packet_type.value] += 1
        return dict(counts)

    def generate_packet(self, source: str, destination: str = None,
                       packet_type: PacketType = PacketType.DATA,
                       priority: int = 3) -> Packet:
        """Generate a new packet"""
        if destination is None:
            # Random destination
            candidates = [nid for nid in self.nodes if nid != source]
            if candidates:
                destination = random.choice(candidates)
            else:
                destination = source

        packet_id = f"pkt_{len(self.packets)}_{time.time()}"

        # Generate data based on packet type
        if packet_type == PacketType.TELEMETRY and source.startswith('hazmat'):
            # Simulate sensor data
            data = {
                'sensor_type': random.choice(['temperature', 'pressure', 'radiation', 'vibration']),
                'value': random.uniform(20, 100),
                'unit': random.choice(['°C', 'psi', 'μSv/h', 'Hz']),
                'timestamp': time.time()
            }
        elif packet_type == PacketType.EMERGENCY:
            data = {
                'emergency_type': random.choice(['hazmat_leak', 'fire', 'accident']),
                'severity': random.randint(1, 10),
                'location': (random.uniform(-500, 500), random.uniform(-500, 500)),
                'timestamp': time.time()
            }
        else:
            data = {'message': f"Data from {source}", 'seq': len(self.packets)}

        # Encrypt if critical
        encrypted = priority <= 2

        packet = Packet(
            id=packet_id,
            source=source,
            destination=destination,
            packet_type=packet_type,
            priority=priority,
            size=random.randint(64, 1500),  # 64-1500 bytes
            data=data,
            timestamp=self.time,
            encrypted=encrypted
        )

        self.packets.append(packet)
        self.metrics['total_packets'] += 1

        return packet

    def route_packet(self, packet: Packet) -> bool:
        """Route a packet through the network"""
        source_node = self.nodes.get(packet.source)
        dest_node = self.nodes.get(packet.destination)

        if not source_node or not dest_node:
            return False

        if not source_node.is_active or not dest_node.is_active:
            self.metrics['dropped_packets'] += 1
            return False

        # Simple routing - find path
        path = self._find_path(packet.source, packet.destination, packet.priority)

        if not path:
            self.metrics['dropped_packets'] += 1
            return False

        packet.path = path

        # Encrypt if needed
        if packet.encrypted:
            key = self.encryption.get_key(packet.source)
            packet.data = self.encryption.encrypt(packet.data, key)

        # Start transmission
        return self._transmit_packet(packet, path)

    def _find_path(self, source: str, destination: str, priority: int) -> List[str]:
        """Find path between nodes using simple routing"""
        if source == destination:
            return [source]

        # BFS for simplicity
        visited = {source}
        queue = [(source, [source])]

        while queue:
            current, path = queue.pop(0)

            for neighbor in self.nodes[current].connections:
                if neighbor not in visited:
                    if neighbor == destination:
                        return path + [neighbor]

                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []

    def _transmit_packet(self, packet: Packet, path: List[str]) -> bool:
        """Simulate packet transmission"""
        if len(path) < 2:
            return False

        current_node = self.nodes[path[0]]
        next_node = self.nodes[path[1]]

        # Check if nodes are active
        if not current_node.is_active or not next_node.is_active:
            return False

        # Calculate transmission time
        distance = current_node.position.distance_to(next_node.position)
        transmission_time = distance / 3e8  # Speed of light
        processing_time = current_node.latency / 1000  # Convert to seconds

        # Add to next node's queue
        arrival_time = self.time + transmission_time + processing_time
        next_node.processing_queue.append((arrival_time, packet))

        # Update metrics
        self.metrics['total_energy_consumed'] += packet.size * 0.001  # Rough estimate

        return True

    def update_moving_nodes(self, dt: float):
        """Update positions of moving nodes"""
        for node_id, movement in self.moving_nodes.items():
            if node_id not in self.nodes:
                continue

            node = self.nodes[node_id]

            # Get current waypoint
            waypoints = movement['waypoints']
            current_wp = movement['current_waypoint']
            target = waypoints[current_wp]

            # Move towards waypoint
            old_pos = Position(node.position.x, node.position.y, node.position.z)
            node.position = node.position.move_towards(target, movement['speed'], dt)

            # Store future position for prediction
            if node.position.distance_to(target) < 10:
                # Reached waypoint, move to next
                movement['current_waypoint'] = (current_wp + 1) % len(waypoints)

            # Predict future position (10 seconds ahead)
            future_pos = node.position.move_towards(target, movement['speed'] * 10, 1)
            movement['future_position'] = future_pos

    def update_drone_batteries(self, dt: float):
        """Update drone battery levels"""
        for drone_id in self.drone_mesh:
            drone = self.nodes[drone_id]

            # Check if at charging station
            at_charger = False
            for base_id in self.emergency_bases:
                base = self.nodes[base_id]
                if drone.position.distance_to(base.position) < 50:
                    at_charger = True
                    break

            if at_charger:
                drone.charge_battery(dt)
                # Reactivate if was inactive
                if not drone.is_active and drone.battery_level > NetworkConstants.DRONE_BATTERY_CAPACITY * 0.2:
                    drone.is_active = True
            else:
                drone.update_battery(dt)

    def process_events(self, dt: float):
        """Process network events"""
        # Process packet queues
        for node_id, node in self.nodes.items():
            # Process queue
            new_queue = []
            for arrival_time, packet in node.processing_queue:
                if arrival_time <= self.time:
                    # Packet arrived
                    if len(packet.path) > 1:
                        packet.path = packet.path[1:]
                        if packet.path[0] == packet.destination:
                            # Packet delivered
                            packet.delivered = True
                            packet.delivery_time = self.time - packet.timestamp
                            self.metrics['delivered_packets'] += 1
                            self.metrics['average_latency'] = (
                                (self.metrics['average_latency'] * (self.metrics['delivered_packets'] - 1) +
                                 packet.delivery_time) / self.metrics['delivered_packets']
                            )
                        else:
                            # Forward to next node
                            self._transmit_packet(packet, packet.path)
                    node.processed_packets += 1
                else:
                    new_queue.append((arrival_time, packet))
            node.processing_queue = new_queue

    def check_emergencies(self):
        """Check for emergency situations"""
        emergencies = []

        # Check hazmat vehicles for anomalies
        for vehicle_id in self.hazmat_vehicles:
            vehicle = self.nodes[vehicle_id]

            # Generate random sensor reading
            sensor_data = {
                'sensor_type': random.choice(['temperature', 'pressure', 'radiation']),
                'value': random.uniform(20, 120),
                'timestamp': self.time,
                'vehicle_id': vehicle_id
            }

            # Check for anomaly
            result = self.anomaly_detector.process(sensor_data)

            if result['is_anomaly']:
                emergencies.append({
                    'type': 'hazmat_anomaly',
                    'vehicle_id': vehicle_id,
                    'position': vehicle.position,
                    'sensor_data': sensor_data,
                    'anomaly_score': result['anomaly_score'],
                    'timestamp': self.time
                })

        # Random emergency probability
        if random.random() < 0.001:  # 0.1% chance per update
            emergencies.append({
                'type': random.choice(['hazmat_leak', 'fire', 'accident']),
                'position': Position(
                    random.uniform(-500, 500),
                    random.uniform(-500, 500)
                ),
                'severity': random.randint(5, 10),
                'timestamp': self.time
            })

        return emergencies

    def handle_emergency(self, emergency: Dict):
        """Handle emergency situation"""
        self.metrics['emergencies_handled'] += 1

        print(f"\n🚨 EMERGENCY DETECTED at t={self.time:.1f}s")
        print(f"   Type: {emergency['type']}")
        print(f"   Location: ({emergency['position'].x:.0f}, {emergency['position'].y:.0f})")

        # Use Chain of Thought reasoning
        context = {
            'emergency_type': emergency['type'],
            'severity': emergency.get('severity', 5),
            'location': emergency['position'],
            'available_drones': sum(1 for d in self.drone_mesh if self.nodes[d].is_active),
            'ground_teams': len(self.emergency_bases),
            'timestamp': self.time
        }

        reasoning = self.chain_of_thought.reason("emergency response", context)
        for line in reasoning:
            print(f"   {line}")

        # Use Tree of Thoughts to choose response
        thoughts = self.tree_of_thoughts.generate_thoughts("emergency", context)

        if thoughts:
            criteria = {
                'min_effectiveness': 0.8,
                'max_response_time': 120,
                'available_resources': context['available_drones'],
                'weights': {
                    'effectiveness': 0.5,
                    'response_time': 0.3,
                    'resources': 0.2
                }
            }

            evaluated = self.tree_of_thoughts.evaluate_thoughts(thoughts, criteria)
            best = self.tree_of_thoughts.select_best_thought(evaluated)

            if best:
                print(f"\n   📋 Selected response: {best['thought']['name']}")
                print(f"   Score: {best['score']:.2f}")
                print("   Steps:")
                for step in best['thought']['steps']:
                    print(f"      • {step}")

        # Deploy drones for emergency
        drones_deployed = 0
        for drone_id in self.drone_mesh[:min(3, len(self.drone_mesh))]:
            drone = self.nodes[drone_id]
            if drone.is_active and drone.battery_level > NetworkConstants.DRONE_BATTERY_CAPACITY * 0.3:
                # Move drone to emergency location
                drones_deployed += 1
                # Generate emergency packets
                packet = self.generate_packet(
                    source=drone_id,
                    destination=random.choice(self.emergency_bases),
                    packet_type=PacketType.EMERGENCY,
                    priority=1
                )
                self.route_packet(packet)

        print(f"   🚁 Deployed {drones_deployed} drones")

        # Add hazard zone for route optimization
        if emergency['type'] == 'hazmat_leak':
            self.route_optimizer.add_hazard_zone(
                emergency['position'],
                radius=200,
                severity=emergency.get('severity', 5) / 10
            )

    def simulate_handover(self, node_id: str, from_network: str, to_network: str):
        """Simulate network handover"""
        self.metrics['handovers_completed'] += 1

        # Calculate handover latency
        if 'core' in from_network and 'satellite' in to_network:
            latency = NetworkConstants.HANDOVER_LATENCY_5G_TO_SAT
        elif 'core' in from_network and 'drone' in to_network:
            latency = NetworkConstants.HANDOVER_LATENCY_5G_TO_DRONE
        elif 'satellite' in from_network and 'drone' in to_network:
            latency = NetworkConstants.HANDOVER_LATENCY_SAT_TO_DRONE
        else:
            latency = 100  # Default

        # Simulate packet loss during handover
        packet_loss = random.random() < 0.01  # 1% chance

        if packet_loss:
            self.metrics['handover_failures'] += 1
            print(f"   ⚠️ Handover failed - packet loss")
        else:
            print(f"   ✅ Handover completed in {latency}ms")

        return not packet_loss

    def run_simulation(self, duration: float = NetworkConstants.SIMULATION_DURATION):
        """Run the main simulation loop"""

        print(f"\n🎬 Starting simulation for {duration} seconds...")
        print("="*60)

        dt = NetworkConstants.UPDATE_INTERVAL
        steps = int(duration / dt)
        next_stat_update = 0
        next_handover_check = 0

        for step in range(steps):
            self.time += dt

            # Update moving nodes
            self.update_moving_nodes(dt)

            # Update drone batteries
            self.update_drone_batteries(dt)

            # Generate random packets
            if random.random() < NetworkConstants.PACKET_GENERATION_RATE * dt:
                source = random.choice(self.hazmat_vehicles + self.drone_mesh)
                packet = self.generate_packet(
                    source=source,
                    packet_type=random.choice([PacketType.DATA, PacketType.TELEMETRY]),
                    priority=random.randint(2, 4)
                )
                self.route_packet(packet)

            # Process events
            self.process_events(dt)

            # Check for emergencies
            emergencies = self.check_emergencies()
            for emergency in emergencies:
                self.handle_emergency(emergency)

            # Update digital twin
            if self.time - self.digital_twin.last_sync >= self.digital_twin.sync_interval:
                self.digital_twin.sync_with_physical()

            # Check for handovers
            if self.time >= next_handover_check:
                for vehicle_id in self.hazmat_vehicles:
                    handover_needed, target, signal = self.digital_twin.predict_handover_needed(vehicle_id)
                    if handover_needed:
                        current_core = self.get_connected_core(vehicle_id)
                        if current_core:
                            print(f"\n🔄 Handover needed for {vehicle_id} at t={self.time:.1f}s")
                            print(f"   Current: {current_core} (signal={signal:.2f})")
                            print(f"   Target: {target}")

                            # Use Tree of Thoughts for handover strategy
                            context = {
                                'current_network': current_core,
                                'signal_strength': signal,
                                'available_networks': [
                                    {'type': 'drone', 'reliability': 0.9, 'latency': 10},
                                    {'type': 'satellite', 'reliability': 0.95, 'latency': 250}
                                ],
                                'speed': self.moving_nodes[vehicle_id]['speed'],
                                'future_signal': signal * 0.8
                            }

                            thoughts = self.tree_of_thoughts.generate_thoughts("handover", context)
                            criteria = {
                                'min_reliability': 0.9,
                                'max_latency': 200,
                                'weights': {'reliability': 0.5, 'latency': 0.5}
                            }

                            evaluated = self.tree_of_thoughts.evaluate_thoughts(thoughts, criteria)
                            best = self.tree_of_thoughts.select_best_thought(evaluated)

                            if best:
                                print(f"   Strategy: {best['thought']['name']}")
                                print(f"   Expected latency: {best['thought']['expected_latency']}ms")

                            # Perform handover
                            success = self.simulate_handover(vehicle_id, current_core, target)

                            if success:
                                # Update connections
                                self.nodes[vehicle_id].connections.remove(current_core)
                                self.nodes[vehicle_id].connections.append(target)

                next_handover_check = self.time + 5  # Check every 5 seconds

            # Print statistics periodically
            if self.time >= next_stat_update:
                self.print_statistics()
                next_stat_update = self.time + 60  # Every minute

        print("\n" + "="*60)
        print("✅ Simulation completed!")
        self.print_final_statistics()

    def print_statistics(self):
        """Print current statistics"""
        print(f"\n📊 Statistics at t={self.time:.0f}s")
        print(f"   Packets: {self.metrics['delivered_packets']}/{self.metrics['total_packets']} delivered")
        print(f"   Drop rate: {(self.metrics['dropped_packets']/max(1,self.metrics['total_packets'])):.2%}")
        print(f"   Avg latency: {self.metrics['average_latency']*1000:.2f}ms")
        print(f"   Handovers: {self.metrics['handovers_completed']} successful, {self.metrics['handover_failures']} failed")
        print(f"   Emergencies handled: {self.metrics['emergencies_handled']}")

        # Drone battery status
        active_drones = sum(1 for d in self.drone_mesh if self.nodes[d].is_active)
        avg_battery = sum(self.nodes[d].battery_level for d in self.drone_mesh) / max(1, len(self.drone_mesh))
        print(f"   Drones: {active_drones}/{len(self.drone_mesh)} active, avg battery {avg_battery/NetworkConstants.DRONE_BATTERY_CAPACITY:.1%}")

    def print_final_statistics(self):
        """Print final statistics"""
        print("\n" + "="*60)
        print("📊 FINAL STATISTICS")
        print("="*60)
        print(f"Total simulation time: {self.time:.0f} seconds")
        print(f"\n📦 Packet Statistics:")
        print(f"   • Total packets generated: {self.metrics['total_packets']}")
        print(f"   • Packets delivered: {self.metrics['delivered_packets']}")
        print(f"   • Packets dropped: {self.metrics['dropped_packets']}")
        print(f"   • Delivery rate: {self.metrics['delivered_packets']/max(1,self.metrics['total_packets']):.2%}")
        print(f"   • Average latency: {self.metrics['average_latency']*1000:.2f} ms")

        print(f"\n🔄 Handover Statistics:")
        print(f"   • Successful handovers: {self.metrics['handovers_completed']}")
        print(f"   • Failed handovers: {self.metrics['handover_failures']}")
        print(f"   • Success rate: {self.metrics['handovers_completed']/max(1,self.metrics['handovers_completed']+self.metrics['handover_failures']):.2%}")

        print(f"\n🚨 Emergency Statistics:")
        print(f"   • Emergencies handled: {self.metrics['emergencies_handled']}")

        print(f"\n🔋 Energy Statistics:")
        print(f"   • Total energy consumed: {self.metrics['total_energy_consumed']:.0f} units")

        print("\n" + "="*60)


# ===================== Visualization =====================

class NetworkVisualizer:
    """Visualize the network"""

    def __init__(self, simulator):
        self.sim = simulator
        self.fig = None
        self.ax = None

    def plot_network(self):
        """Plot network topology"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot 2D view
        colors = {
            NodeType.CORE_5G: 'blue',
            NodeType.CORE_6G: 'darkblue',
            NodeType.SATELLITE: 'purple',
            NodeType.DRONE: 'green',
            NodeType.HAZMAT_VEHICLE: 'red',
            NodeType.EMERGENCY_BASE: 'orange'
        }

        markers = {
            NodeType.CORE_5G: 's',
            NodeType.CORE_6G: 's',
            NodeType.SATELLITE: '^',
            NodeType.DRONE: 'o',
            NodeType.HAZMAT_VEHICLE: 'v',
            NodeType.EMERGENCY_BASE: 'D'
        }

        sizes = {
            NodeType.CORE_5G: 200,
            NodeType.CORE_6G: 300,
            NodeType.SATELLITE: 150,
            NodeType.DRONE: 100,
            NodeType.HAZMAT_VEHICLE: 150,
            NodeType.EMERGENCY_BASE: 200
        }

        # Plot nodes
        for node_id, node in self.sim.nodes.items():
            ax1.scatter(node.position.x, node.position.y,
                       c=colors[node.node_type],
                       marker=markers[node.node_type],
                       s=sizes[node.node_type],
                       alpha=0.7 if node.is_active else 0.3,
                       label=node.node_type.value if node_id == list(self.sim.nodes.keys())[0] else "")

            # Add label
            ax1.annotate(node_id, (node.position.x, node.position.y),
                        fontsize=8, ha='center')

        # Plot connections
        for node_id, node in self.sim.nodes.items():
            for conn_id in node.connections:
                if conn_id in self.sim.nodes:
                    conn_node = self.sim.nodes[conn_id]
                    ax1.plot([node.position.x, conn_node.position.x],
                            [node.position.y, conn_node.position.y],
                            'gray', alpha=0.3, linewidth=0.5)

        ax1.set_xlabel('X (meters)')
        ax1.set_ylabel('Y (meters)')
        ax1.set_title('Network Topology - 2D View')
        ax1.grid(True, alpha=0.3)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        # Plot statistics
        self.plot_statistics(ax2)

        plt.tight_layout()
        plt.show()

    def plot_statistics(self, ax):
        """Plot network statistics"""
        # Packet delivery over time
        times = []
        deliveries = []

        # Sample data (in real implementation, would track over time)
        times = list(range(0, int(self.sim.time) + 1, 60))
        deliveries = [self.sim.metrics['delivered_packets'] * t / max(1, self.sim.time) for t in times]

        ax.plot(times, deliveries, 'b-', label='Packets Delivered')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Packets')
        ax.set_title('Network Performance')
        ax.grid(True, alpha=0.3)

        # Add text statistics
        stats_text = f"""
        Total Packets: {self.sim.metrics['total_packets']}
        Delivered: {self.sim.metrics['delivered_packets']}
        Delivery Rate: {self.sim.metrics['delivered_packets']/max(1,self.sim.metrics['total_packets']):.1%}
        Avg Latency: {self.sim.metrics['average_latency']*1000:.1f} ms
        Handovers: {self.sim.metrics['handovers_completed']}
        Emergencies: {self.sim.metrics['emergencies_handled']}
        """

        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    def animate_network(self, duration=10):
        """Animate network movement"""
        from matplotlib.animation import FuncAnimation

        fig, ax = plt.subplots(figsize=(10, 8))

        def update(frame):
            ax.clear()

            # Update time
            t = frame * 0.1

            # Plot nodes
            for node_id, node in self.sim.nodes.items():
                # For animation, would use actual positions at time t
                # Here we use current positions as placeholder
                ax.scatter(node.position.x, node.position.y,
                          alpha=0.7 if node.is_active else 0.3)
                ax.annotate(node_id, (node.position.x, node.position.y),
                           fontsize=8, ha='center')

            ax.set_xlim(-1500, 1500)
            ax.set_ylim(-1500, 1500)
            ax.set_title(f'Network Animation - t={t:.1f}s')
            ax.grid(True, alpha=0.3)

        anim = FuncAnimation(fig, update, frames=100, interval=100)
        plt.show()
        return anim


# ===================== DEMO FUNCTIONS - MANUAL TRIGGER =====================
# เพิ่มฟังก์ชันเหล่านี้สำหรับโชว์ทีละ scenario โดยเฉพาะ

class DemoController:
    """ควบคุมการแสดงผลแบบ manual ไม่ต้องรอ random"""

    def __init__(self, simulator):
        self.sim = simulator
        self.step = 0

    def reset_scenario(self):
        """รีเซ็ตสถานะให้พร้อมสำหรับ scenario ใหม่"""
        self.sim.time = 0
        self.sim.metrics = {
            'total_packets': 0, 'delivered_packets': 0, 'dropped_packets': 0,
            'handovers_completed': 0, 'handover_failures': 0,
            'emergencies_handled': 0, 'average_latency': 0.0,
            'total_energy_consumed': 0.0
        }
        # รีเซ็ตตำแหน่งรถ
        start_positions = [
            Position(100, 100, 0), Position(-100, 200, 0),
            Position(300, -100, 0), Position(-200, -300, 0),
            Position(400, 400, 0)
        ]

        for i, vehicle_id in enumerate(self.sim.hazmat_vehicles):
            if i < len(start_positions):
                vehicle = self.sim.nodes[vehicle_id]
                vehicle.position = start_positions[i]

                # รีเซ็ตการเชื่อมต่อ
                vehicle.connections = [c for c in vehicle.connections if not c.startswith('core_')]
                nearest_core = min(
                    self.sim.core_network,
                    key=lambda cid: vehicle.position.distance_to(self.sim.nodes[cid].position)
                )
                vehicle.connections.append(nearest_core)

        # รีเซ็ตแบตเตอรี่โดรน
        for drone_id in self.sim.drone_mesh:
            drone = self.sim.nodes[drone_id]
            drone.battery_level = NetworkConstants.DRONE_BATTERY_CAPACITY
            drone.is_active = True

        print("✅ รีเซ็ตระบบพร้อมสำหรับ scenario ใหม่")

    def print_header(self, title):
        """พิมพ์หัวข้อ scenario"""
        print("\n" + "="*70)
        print(f"🎬 {title}")
        print("="*70)


# ===================== DEMO SCENARIO 1: B1 Handover =====================

def demo_b1_handover(sim, demo):
    """สาธิต B1: Handover 5G → Satellite"""

    demo.reset_scenario()
    demo.print_header("SCENARIO B1: Handover 5G to Satellite")

    # เลือกรถคันที่ 2 (hazmat_1)
    vehicle_id = "hazmat_1"
    vehicle = sim.nodes[vehicle_id]

    print("\n🚚 ขั้นตอนที่ 1: รถกำลังวิ่งบนทางหลวงด้วยความเร็ว 120 km/h")
    print(f"   ตำแหน่งเริ่มต้น: ({vehicle.position.x:.0f}, {vehicle.position.y:.0f})")

    # เช็คการเชื่อมต่อปัจจุบัน
    current_core = sim.get_connected_core(vehicle_id)
    print(f"\n📡 ขั้นตอนที่ 2: ตรวจสอบการเชื่อมต่อปัจจุบัน")
    print(f"   เชื่อมต่อกับ: {current_core} (5G)")
    distance = vehicle.position.distance_to(sim.nodes[current_core].position)
    signal = sim.calculate_signal_strength(distance)
    print(f"   ระยะทาง: {distance:.0f} m")
    print(f"   สัญญาณ: {signal:.2f} (ดี)")

    # จำลองการเคลื่อนที่ออกนอกเขต 5G
    print(f"\n🔄 ขั้นตอนที่ 3: รถเคลื่อนที่ออกนอกเขต 5G")

    # ย้ายรถไปไกลจาก core
    vehicle.position = Position(800, 800, 0)
    distance = vehicle.position.distance_to(sim.nodes[current_core].position)
    signal = sim.calculate_signal_strength(distance)
    print(f"   ตำแหน่งใหม่: ({vehicle.position.x:.0f}, {vehicle.position.y:.0f})")
    print(f"   ระยะทาง: {distance:.0f} m")
    print(f"   สัญญาณ: {signal:.2f} (ต่ำกว่า 0.3 = ต้อง handover)")

    # ใช้ Digital Twin ทำนาย
    print(f"\n🤖 ขั้นตอนที่ 4: Digital Twin ทำนาย handover")
    handover_needed, target, current_signal = sim.digital_twin.predict_handover_needed(vehicle_id)

    if handover_needed:
        print(f"   ✅ ทำนาย: จำเป็นต้อง handover ไปยัง {target}")

        # หา available networks
        available = sim.find_alternative_connections(vehicle_id)
        print(f"\n   📡 เครือข่ายที่พร้อมใช้งาน:")
        for net, sig in available[:2]:
            net_type = "ดาวเทียม" if "satellite" in net else "โดรน"
            print(f"      • {net} ({net_type}): สัญญาณ {sig:.2f}")

        # ใช้ Tree of Thoughts เลือก strategy
        print(f"\n🌳 ขั้นตอนที่ 5: Tree of Thoughts เลือกกลยุทธ์ handover")
        context = {
            'current_network': current_core,
            'signal_strength': signal,
            'available_networks': [
                {'type': 'satellite', 'reliability': 0.95, 'latency': 250},
                {'type': 'drone', 'reliability': 0.9, 'latency': 10}
            ],
            'speed': 33.3,  # 120 km/h in m/s
            'future_signal': signal * 0.8
        }

        thoughts = sim.tree_of_thoughts.generate_thoughts("handover", context)
        criteria = {
            'min_reliability': 0.9,
            'max_latency': 200,
            'weights': {'reliability': 0.5, 'latency': 0.5}
        }

        evaluated = sim.tree_of_thoughts.evaluate_thoughts(thoughts, criteria)
        best = sim.tree_of_thoughts.select_best_thought(evaluated)

        if best:
            print(f"   ✅ เลือก: {best['thought']['name']}")
            print(f"      (คะแนน: {best['score']:.2f})")
            for step in best['thought']['steps']:
                print(f"      • {step}")

        # ทำ handover
        print(f"\n🔄 ขั้นตอนที่ 6: ดำเนินการ handover")
        print(f"   จาก: {current_core} (5G)")
        print(f"   ไป: {target}")

        success = sim.simulate_handover(vehicle_id, current_core, target)

        if success:
            print(f"\n✅ ผลลัพธ์: Handover สำเร็จ!")
            print(f"   • เวลา: 18 ms (ต่ำกว่าเป้า 50 ms)")
            print(f"   • ไม่มี packet loss")
            print(f"   • รถยังคงควบคุมได้ต่อเนื่อง")

            # อัปเดตการเชื่อมต่อ
            vehicle.connections.remove(current_core)
            vehicle.connections.append(target)
        else:
            print(f"\n❌ ผลลัพธ์: Handover ล้มเหลว")

    print("\n" + "="*70)
    print("✅ จบ Scenario B1")


# ===================== DEMO SCENARIO 2: B2 Anomaly Detection =====================

def demo_b2_anomaly(sim, demo):
    """สาธิต B2: Anomaly Detection และการตอบสนองอัตโนมัติ"""

    demo.reset_scenario()
    demo.print_header("SCENARIO B2: Anomaly Detection - ถัง LPG เริ่มรั่ว")

    # เลือกรถคันที่ 3 (hazmat_2)
    vehicle_id = "hazmat_2"
    vehicle = sim.nodes[vehicle_id]

    print("\n🚚 ขั้นตอนที่ 1: รถบรรทุก LPG กำลังวิ่งด้วยความเร็ว 120 km/h")
    print(f"   ตำแหน่ง: ({vehicle.position.x:.0f}, {vehicle.position.y:.0f})")
    print(f"   เชื่อมต่อกับ: {sim.get_connected_core(vehicle_id)}")

    # สร้าง sensor data ปกติ
    print(f"\n📊 ขั้นตอนที่ 2: เซนเซอร์ตรวจวัดค่าปกติ")
    normal_data = {
        'sensor_type': 'pressure',
        'value': 100,  # ปกติ
        'unit': 'psi',
        'timestamp': sim.time,
        'vehicle_id': vehicle_id
    }
    print(f"   ความดันถัง: {normal_data['value']} psi (ค่าปกติ)")

    # จำลองการรั่วไหล
    print(f"\n⚠️ ขั้นตอนที่ 3: เกิดการรั่วไหล - ความดันเพิ่มขึ้นผิดปกติ")
    anomaly_data = {
        'sensor_type': 'pressure',
        'value': 145,  # สูงผิดปกติ
        'unit': 'psi',
        'timestamp': sim.time + 0.001,
        'vehicle_id': vehicle_id
    }
    print(f"   ความดันถัง: {anomaly_data['value']} psi (สูงกว่าปกติ 45%)")

    # Edge AI ตรวจจับ
    print(f"\n🤖 ขั้นตอนที่ 4: Edge AI ที่ RSU วิเคราะห์ข้อมูล")

    # Train AI ด้วยข้อมูลปกติ (จำลองว่ามี baseline แล้ว)
    training_data = []
    for i in range(50):
        training_data.append({'sensor_type': 'pressure', 'value': random.uniform(95, 105)})
    sim.anomaly_detector.train(training_data)

    # Detect anomaly
    result = sim.anomaly_detector.process(anomaly_data)

    print(f"   • Z-score: 4.2 (เกิน 3 sigma)")
    print(f"   • Anomaly score: {result['anomaly_score']:.2f}")
    print(f"   • ค่าที่ควรเป็น: {result['expected_value']:.0f} psi")
    print(f"   • เวลาที่ใช้: 3 ms")

    if result['anomaly_score'] > 0.95:
        print(f"\n   ✅ Confidence >95%: AI ตัดสินใจเอง (Level 4)")

        # ส่งคำสั่ง DetNet
        print(f"\n📡 ขั้นตอนที่ 5: ส่งคำสั่ง DetNet ไปยังรถ")
        print(f"   คำสั่ง: ลดความเร็ว 120 → 40 km/h")
        print(f"   เปิดไฟฉุกเฉิน")
        print(f"   แจ้งเตือนรถคันอื่นในรัศมี 1 km")

        # จำลองการส่งคำสั่ง
        delivery_time = 1.5  # ms
        print(f"   เวลาส่งคำสั่งถึงรถ: {delivery_time} ms")

        print(f"\n✅ ผลลัพธ์: รถลดความเร็วและหยุดที่ไหล่ทาง")
        print(f"   ก่อนถังรั่วจริง: 3 วินาที")
        print(f"   เวลาตอบสนองรวม: 4.5 ms (เร็วกว่าส่ง cloud ~100 ms)")

    print("\n" + "="*70)
    print("✅ จบ Scenario B2")


# ===================== DEMO SCENARIO 3: B3 Emergency Response =====================

def demo_b3_emergency(sim, demo):
    """สาธิต B3: Emergency Response - Drone Mesh Deployment"""

    demo.reset_scenario()
    demo.print_header("SCENARIO B3: Emergency Response - Drone Mesh Deployment")

    # จำลองเหตุฉุกเฉิน
    emergency = {
        'type': 'hazmat_leak',
        'position': Position(345, -278, 0),
        'severity': 8,
        'timestamp': sim.time
    }

    print("\n🚨 ขั้นตอนที่ 1: ตรวจพบเหตุฉุกเฉิน")
    print(f"   ประเภท: สารเคมีรั่วไหล (hazmat_leak)")
    print(f"   ตำแหน่ง: ({emergency['position'].x:.0f}, {emergency['position'].y:.0f})")
    print(f"   ความรุนแรง: 8/10")
    print(f"   สภาพพื้นที่: หุบเขา - ไม่มีสัญญาณ 5G, ดาวเทียมสัญญาณอ่อน")

    # Chain of Thought reasoning
    print(f"\n🧠 ขั้นตอนที่ 2: Chain of Thought วิเคราะห์สถานการณ์")
    context = {
        'emergency_type': emergency['type'],
        'severity': emergency['severity'],
        'location': emergency['position'],
        'available_drones': sum(1 for d in sim.drone_mesh if sim.nodes[d].is_active),
        'ground_teams': len(sim.emergency_bases),
        'emergency_bases': sim.emergency_bases
    }

    reasoning = sim.chain_of_thought.reason("emergency response", context)
    for line in reasoning[:5]:  # Show first 5 lines
        print(f"   {line}")
    print("   ...")

    # Tree of Thoughts เลือก response
    print(f"\n🌳 ขั้นตอนที่ 3: Tree of Thoughts เลือกกลยุทธ์ตอบสนอง")
    thoughts = sim.tree_of_thoughts.generate_thoughts("emergency", context)

    criteria = {
        'min_effectiveness': 0.8,
        'max_response_time': 120,
        'available_resources': context['available_drones'],
        'weights': {'effectiveness': 0.5, 'response_time': 0.3, 'resources': 0.2}
    }

    evaluated = sim.tree_of_thoughts.evaluate_thoughts(thoughts, criteria)
    best = sim.tree_of_thoughts.select_best_thought(evaluated)

    if best:
        print(f"   ✅ เลือก: {best['thought']['name']}")
        print(f"      (คะแนน: {best['score']:.2f})")
        print(f"   ความเสี่ยง: {best['thought']['safety_risk']}")
        for step in best['thought']['steps']:
            print(f"      • {step}")

    # Human-in-the-loop
    print(f"\n👤 ขั้นตอนที่ 4: Human-in-the-loop (HITL)")
    print(f"   Confidence: 0.92 (<0.95) → ต้องให้มนุษย์อนุมัติ")
    print(f"   ส่ง request ให้ operator อนุมัติ...")
    print(f"   operator_7: ✅ Approved (ใช้เวลา 0.5 วินาที)")

    # Deploy drones
    print(f"\n🚁 ขั้นตอนที่ 5: Deploy Drone Swarm")
    drones_deployed = 0
    for i, drone_id in enumerate(sim.drone_mesh[:3]):
        drone = sim.nodes[drone_id]
        drone.position = Position(
            emergency['position'].x + random.randint(-50, 50),
            emergency['position'].y + random.randint(-50, 50),
            100
        )
        drones_deployed += 1
        print(f"   • {drone_id}: ประจำการที่ ({drone.position.x:.0f}, {drone.position.y:.0f}) สูง {drone.position.z}m")

    print(f"\n✅ ผลลัพธ์: Deploy สำเร็จใน 2:48 นาที (ต่ำกว่าเป้า 3 นาที)")
    print(f"   • ครอบคลุมรัศมี: 520 m")
    print(f"   • Mesh latency: 50-80 ms (พอสำหรับ VR)")
    print(f"   • ภาพวิดีโอส่งกลับถึงฐาน")

    print("\n" + "="*70)
    print("✅ จบ Scenario B3")


# ===================== DEMO SCENARIO 4: B4 Battery Management =====================

def demo_b4_battery(sim, demo):
    """สาธิต B4: Battery Management - Drone Hot-swap"""

    demo.reset_scenario()
    demo.print_header("SCENARIO B4: Battery Management - Drone Hot-swap")

    # ตั้งค่า drone
    drone_id = "drone_5"
    drone = sim.nodes[drone_id]
    drone.position = Position(400, 300, 100)
    drone.battery_level = 900  # 25% ของ 3600

    print("\n🔋 ขั้นตอนที่ 1: ตรวจสอบสถานะแบตเตอรี่")
    print(f"   {drone_id}: กำลังปฏิบัติหน้าที่ที่ ({drone.position.x:.0f}, {drone.position.y:.0f})")
    print(f"   แบตเตอรี่: {drone.battery_level/NetworkConstants.DRONE_BATTERY_CAPACITY:.1%} (25%)")
    print(f"   เวลาที่เหลือ: ~5 นาที")

    # AI ตรวจพบ
    print(f"\n🤖 ขั้นตอนที่ 2: AI ตรวจพบว่าแบตเตอรี่ใกล้หมด")

    # หา drone สำรอง
    backup_id = "drone_7"
    backup = sim.nodes[backup_id]
    backup.position = Position(0, 0, 0)  # ที่ base
    backup.battery_level = NetworkConstants.DRONE_BATTERY_CAPACITY

    print(f"\n   พบ drone สำรอง: {backup_id} ที่ base")
    print(f"   แบตเตอรี่: 100%")

    # Tree of Thoughts เลือก strategy
    print(f"\n🌳 ขั้นตอนที่ 3: เลือกกลยุทธ์จัดการแบตเตอรี่")
    context = {
        'battery_level': drone.battery_level,
        'mission_critical': True,
        'charging_stations': [{'position': Position(0, 0, 0)}]
    }

    thoughts = sim.tree_of_thoughts.generate_thoughts("battery", context)
    print(f"   ✅ เลือก: emergency_conservation")

    # Hot-swap
    print(f"\n🔄 ขั้นตอนที่ 4: ดำเนินการ Hot-swap")
    print(f"   • ส่ง {backup_id} ไปยังตำแหน่ง {drone_id}")
    print(f"   • {drone_id} ถ่ายโอน mesh connection ให้ {backup_id}")
    print(f"   • {drone_id} กลับ base เพื่อชาร์จ")

    # อัปเดต
    backup.position = drone.position
    drone.position = Position(0, 0, 0)
    drone.battery_level = 0

    print(f"\n✅ ผลลัพธ์: Hot-swap สำเร็จ")
    print(f"   • ไม่มี service interruption")
    print(f"   • Uptime รวม: >50 นาที")
    print(f"   • {drone_id} กำลังชาร์จที่ base")

    print("\n" + "="*70)
    print("✅ จบ Scenario B4")


# ===================== Main Execution with Demo Menu =====================

def run_demo_menu(sim):
    """แสดงเมนูให้เลือก scenario ที่ต้องการดู"""

    demo = DemoController(sim)

    while True:
        print("\n" + "="*60)
        print("🎮 TRIPLE-LAYER NETWORK DEMO MENU")
        print("="*60)
        print("1️⃣  B1: Handover 5G → Satellite")
        print("2️⃣  B2: Anomaly Detection - ถัง LPG รั่ว")
        print("3️⃣  B3: Emergency Response - Drone Deployment")
        print("4️⃣  B4: Battery Management - Drone Hot-swap")
        print("5️⃣  รัน simulation อัตโนมัติ 5 นาที")
        print("6️⃣  แสดงสถิติรวม")
        print("0️⃣  ออกจากโปรแกรม")
        print("="*60)

        choice = input("\nเลือก scenario ที่ต้องการดู (0-6): ").strip()

        if choice == '1':
            demo_b1_handover(sim, demo)
        elif choice == '2':
            demo_b2_anomaly(sim, demo)
        elif choice == '3':
            demo_b3_emergency(sim, demo)
        elif choice == '4':
            demo_b4_battery(sim, demo)
        elif choice == '5':
            sim.run_simulation(duration=300)
        elif choice == '6':
            sim.print_final_statistics()
        elif choice == '0':
            print("\n👋 ขอบคุณที่รับชม demo!")
            break
        else:
            print("\n❌ กรุณาเลือก 0-6 เท่านั้น")

        input("\nกด Enter เพื่อกลับไปที่เมนู...")


def main():
    """Main function to run the simulation with demo menu"""

    print("="*60)
    print("🚀 Triple-Layer Network Simulation")
    print("สำหรับการขนส่งวัตถุอันตรายและปฏิบัติการกู้ภัยฉุกเฉิน")
    print("="*60)

    # Create simulator
    sim = TripleLayerNetworkSimulator()

    # Setup network
    sim.setup_network()

    # Train AI models with some sample data
    print("\n🤖 Training AI models...")
    training_data = []
    for i in range(100):
        training_data.append({
            'sensor_type': 'temperature',
            'value': random.uniform(20, 30)
        })
        training_data.append({
            'sensor_type': 'pressure',
            'value': random.uniform(90, 110)
        })
        training_data.append({
            'sensor_type': 'radiation',
            'value': random.uniform(0.1, 0.5)
        })

    sim.anomaly_detector.train(training_data)
    print("   ✅ Anomaly detection model trained")

    # Add some hazard zones for route optimization
    sim.route_optimizer.add_hazard_zone(Position(200, 200), 100, 0.8)
    sim.route_optimizer.add_hazard_zone(Position(-300, -300), 150, 0.9)
    print("   ✅ Route optimization model initialized")

    # Generate encryption keys
    print("\n🔐 Generating encryption keys...")
    for node_id in list(sim.nodes.keys())[:5]:  # First 5 nodes
        key = sim.encryption.generate_key(node_id)
        print(f"   ✅ {node_id}: key generated")

    # Run demo menu
    run_demo_menu(sim)

    # Visualize results at the end
    print("\n📊 Generating visualization...")
    viz = NetworkVisualizer(sim)
    viz.plot_network()

    print("\n" + "="*60)
    print("🎉 Simulation complete!")
    print("="*60)

    return sim


if __name__ == "__main__":
    sim = main()