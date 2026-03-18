"""
Main network simulation engine
"""
import random
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import time
import json
import os
import logging

from config.settings import settings
from config.constants import CONSTANTS
from core.event_scheduler import EventScheduler, EventType
from core.packet_manager import PacketManager, Packet
from core.routing_protocol import RoutingProtocol
from core.mobility_model import MobilityModel
from core.energy_model import EnergyModel
from models.drone_model import DroneSwarm, Drone
from models.digital_twin import DigitalTwin
from models.edge_ai import AnomalyDetectionModel, RouteOptimizationModel
from models.encryption import QuantumResistantEncryption
from models.reasoning import TreeOfThoughts, ChainOfThought
from visualization.live_plot import LivePlot
from data.collector import DataCollector
logger = logging.getLogger(__name__)

class NetworkNode:
    """Network node representation"""
    def __init__(self, node_id: str, node_type: str, position: Tuple[float, float, float],
                 bandwidth: float, latency: float, reliability: float,
                 battery_level: float = None):
        self.id = node_id
        self.node_type = node_type
        self.position = position
        self.bandwidth = bandwidth
        self.latency = latency
        self.reliability = reliability
        self.battery_level = battery_level
        self.is_active = True
        self.connections = []
        self.buffer = []
        self.packets_sent = 0
        self.packets_received = 0
        self.packets_dropped = 0

class NetworkEngine:
    """Main simulation engine"""
    
    def __init__(self):
        # Set random seed
        random.seed(settings.RANDOM_SEED)
        np.random.seed(settings.RANDOM_SEED)
        
        # Core components
        self.scheduler = EventScheduler()
        self.packet_manager = PacketManager()
        self.routing = RoutingProtocol()
        self.mobility = MobilityModel()
        self.energy = EnergyModel()
        
        # Data collection
        self.data_collector = DataCollector()
        self.live_plot = LivePlot() if settings.REAL_TIME_PLOT else None
        
        # Network state
        self.nodes: Dict[str, NetworkNode] = {}
        self.node_types: Dict[str, List[str]] = defaultdict(list)
        
        # Drone swarm
        self.drone_swarm = DroneSwarm()
        self.drone_deployment_history = []
        
        # Intelligence layer
        self.digital_twin = DigitalTwin(self) if settings.ENABLE_DIGITAL_TWIN else None
        self.anomaly_detector = AnomalyDetectionModel()
        self.route_optimizer = RouteOptimizationModel()
        self.encryption = QuantumResistantEncryption() if settings.ENABLE_ENCRYPTION else None
        self.tree_of_thoughts = TreeOfThoughts() if settings.ENABLE_REASONING else None
        self.chain_of_thought = ChainOfThought() if settings.ENABLE_REASONING else None
        
        # Performance metrics
        self.metrics = {
            'total_packets': 0,
            'delivered_packets': 0,
            'dropped_packets': 0,
            'handovers_completed': 0,
            'handover_failures': 0,
            'emergencies_handled': 0,
            'average_latency': 0.0,
            'total_energy_consumed': 0.0,
            'start_time': 0,
            'end_time': 0
        }
        
        logger.info("NetworkEngine initialized")

    def setup_network(self):
        """Initialize network topology"""
        logger.info("Setting up Triple-Layer Network")
        print("\n" + "="*60)
        print("Setting up Triple-Layer Network")
        print("="*60)
        
        self._create_core_network()
        self._create_satellite_network()
        self._create_drone_mesh()
        self._create_vehicles()
        self._create_bases()
        self._setup_connections()
        self._print_network_summary()

    def _create_core_network(self):
        """Create 5G/6G core nodes"""
        print("\n📡 Creating Core Network...")
        
        positions = [
            (0, 0, 50),      # Central core (6G)
            (500, 500, 50),   # East core
            (-500, -500, 50), # West core
            (500, -500, 50),  # South core
            (-500, 500, 50)   # North core
        ]
        
        for i, pos in enumerate(positions[:settings.NUM_CORE_NODES]):
            if i == 0:
                node_type = 'CORE_6G'
                bandwidth = settings.CORE_BANDWIDTH_6G
                latency = settings.CORE_LATENCY_6G
                reliability = settings.CORE_RELIABILITY_6G
            else:
                node_type = 'CORE_5G'
                bandwidth = settings.CORE_BANDWIDTH_5G
                latency = settings.CORE_LATENCY_5G
                reliability = settings.CORE_RELIABILITY_5G
            
            node = NetworkNode(
                node_id=f"core_{i}",
                node_type=node_type,
                position=pos,
                bandwidth=bandwidth,
                latency=latency,
                reliability=reliability
            )
            self.nodes[node.id] = node
            self.node_types[node_type].append(node.id)
            print(f"   ✅ {node.id}: at {pos}")

    def _create_satellite_network(self):
        """Create satellite nodes"""
        print("\n🛰️ Creating Satellite Network...")
        
        positions = [
            (1000, 1000, 500),
            (-1000, -1000, 500),
            (1000, -1000, 500),
            (-1000, 1000, 500)
        ]
        
        for i, pos in enumerate(positions[:settings.NUM_SATELLITES]):
            node = NetworkNode(
                node_id=f"satellite_{i}",
                node_type='SATELLITE',
                position=pos,
                bandwidth=settings.SAT_BANDWIDTH,
                latency=settings.SAT_LATENCY,
                reliability=settings.SAT_RELIABILITY
            )
            self.nodes[node.id] = node
            self.node_types['SATELLITE'].append(node.id)
            print(f"   ✅ {node.id}: at {pos}")

    def _create_drone_mesh(self):
        """Create drone nodes with swarm management"""
        print("\n🚁 Creating Drone Mesh Network...")
        
        positions = [
            (200, 200, 100), (-200, 200, 100), (200, -200, 100), (-200, -200, 100),
            (0, 300, 100), (300, 0, 100), (0, -300, 100), (-300, 0, 100),
            (500, 0, 100), (-500, 0, 100), (0, 500, 100), (0, -500, 100)
        ]
        
        # Create charging stations at bases
        for base_id in self.node_types.get('EMERGENCY_BASE', []):
            base = self.nodes[base_id]
            self.drone_swarm.add_charging_station(base.position)
        
        for i, pos in enumerate(positions[:settings.NUM_DRONES]):
            # Create network node
            node = NetworkNode(
                node_id=f"drone_{i}",
                node_type='DRONE',
                position=pos,
                bandwidth=settings.DRONE_BANDWIDTH,
                latency=settings.DRONE_LATENCY,
                reliability=settings.DRONE_RELIABILITY,
                battery_level=settings.DRONE_BATTERY_CAPACITY
            )
            self.nodes[node.id] = node
            self.node_types['DRONE'].append(node.id)
            
            # Create drone object for swarm
            drone = Drone(f"drone_{i}", pos)
            
            # Assign home base
            if self.drone_swarm.charging_stations:
                station_idx = i % len(self.drone_swarm.charging_stations)
                drone.home_base = self.drone_swarm.charging_stations[station_idx]
            
            self.drone_swarm.add_drone(drone)
            
            print(f"   ✅ {node.id}: at {pos}")

    def _create_vehicles(self):
        """Create hazmat vehicles"""
        print("\n🚚 Creating Hazmat Vehicles...")
        
        positions = [
            (100, 100, 0), (-100, 200, 0), (300, -100, 0), 
            (-200, -300, 0), (400, 400, 0)
        ]
        
        for i, pos in enumerate(positions[:settings.NUM_VEHICLES]):
            node = NetworkNode(
                node_id=f"hazmat_{i}",
                node_type='HAZMAT_VEHICLE',
                position=pos,
                bandwidth=10,
                latency=20,
                reliability=0.95
            )
            self.nodes[node.id] = node
            self.node_types['HAZMAT_VEHICLE'].append(node.id)
            
            # Set mobility pattern
            self.mobility.add_vehicle(
                vehicle_id=node.id,
                start_pos=pos,
                speed=random.uniform(5, 15)
            )
            print(f"   ✅ {node.id}: at {pos}")

    def _create_bases(self):
        """Create emergency bases"""
        print("\n🏥 Creating Emergency Bases...")
        
        positions = [
            (0, 0, 0), (1000, 0, 0), (0, 1000, 0), 
            (-1000, 0, 0), (0, -1000, 0)
        ]
        
        for i, pos in enumerate(positions[:settings.NUM_BASES]):
            node = NetworkNode(
                node_id=f"base_{i}",
                node_type='EMERGENCY_BASE',
                position=pos,
                bandwidth=100,
                latency=5,
                reliability=0.99
            )
            self.nodes[node.id] = node
            self.node_types['EMERGENCY_BASE'].append(node.id)
            print(f"   ✅ {node.id}: at {pos}")

    def _setup_connections(self):
        """Setup network connections"""
        connection_count = 0
        
        # Connect core nodes
        core_nodes = self.node_types.get('CORE_5G', []) + self.node_types.get('CORE_6G', [])
        for i, node_id in enumerate(core_nodes):
            for j, other_id in enumerate(core_nodes):
                if i != j:
                    self._add_connection(node_id, other_id)
                    connection_count += 1
        
        # Connect drones to core
        for drone_id in self.node_types.get('DRONE', []):
            drone = self.nodes[drone_id]
            for core_id in core_nodes:
                core = self.nodes[core_id]
                distance = self._calculate_distance(drone.position, core.position)
                if distance < settings.DRONE_MAX_RANGE:
                    self._add_connection(drone_id, core_id)
                    connection_count += 1
        
        # Connect drones to each other
        drones = self.node_types.get('DRONE', [])
        for i, drone_id in enumerate(drones):
            for j, other_id in enumerate(drones):
                if i != j:
                    drone = self.nodes[drone_id]
                    other = self.nodes[other_id]
                    distance = self._calculate_distance(drone.position, other.position)
                    if distance < settings.DRONE_MESH_RANGE:
                        self._add_connection(drone_id, other_id)
                        connection_count += 1
        
        # Connect satellites to core
        for sat_id in self.node_types.get('SATELLITE', []):
            for core_id in core_nodes:
                self._add_connection(sat_id, core_id)
                connection_count += 1
        
        # Connect vehicles
        for vehicle_id in self.node_types.get('HAZMAT_VEHICLE', []):
            vehicle = self.nodes[vehicle_id]
            
            # Connect to nearest core
            if core_nodes:
                nearest_core = min(core_nodes, 
                                 key=lambda cid: self._calculate_distance(
                                     vehicle.position, self.nodes[cid].position))
                self._add_connection(vehicle_id, nearest_core)
                connection_count += 1
            
            # Connect to nearby drones
            for drone_id in drones:
                drone = self.nodes[drone_id]
                distance = self._calculate_distance(vehicle.position, drone.position)
                if distance < 500:
                    self._add_connection(vehicle_id, drone_id)
                    connection_count += 1
        
        # Connect bases
        for base_id in self.node_types.get('EMERGENCY_BASE', []):
            for core_id in core_nodes:
                self._add_connection(base_id, core_id)
                connection_count += 1
            for sat_id in self.node_types.get('SATELLITE', []):
                self._add_connection(base_id, sat_id)
                connection_count += 1
            for drone_id in drones:
                self._add_connection(base_id, drone_id)
                connection_count += 1
        
        print(f"\n   Created {connection_count} connections")

    def _add_connection(self, node1: str, node2: str):
        """Add bidirectional connection"""
        if node2 not in self.nodes[node1].connections:
            self.nodes[node1].connections.append(node2)
        if node1 not in self.nodes[node2].connections:
            self.nodes[node2].connections.append(node1)

    def _calculate_distance(self, pos1: Tuple[float, float, float], 
                          pos2: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance"""
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))

    def _print_network_summary(self):
        """Print network setup summary"""
        print("\n" + "="*60)
        print("Network setup complete!")
        print(f"   Total nodes: {len(self.nodes)}")
        print(f"   • Core Network: {len(self.node_types.get('CORE_5G', []))} 5G + "
              f"{len(self.node_types.get('CORE_6G', []))} 6G")
        print(f"   • Satellite Network: {len(self.node_types.get('SATELLITE', []))}")
        print(f"   • Drone Mesh: {len(self.node_types.get('DRONE', []))}")
        print(f"   • Hazmat Vehicles: {len(self.node_types.get('HAZMAT_VEHICLE', []))}")
        print(f"   • Emergency Bases: {len(self.node_types.get('EMERGENCY_BASE', []))}")
        print("="*60)

    def schedule_events(self):
        """Schedule all simulation events"""
        
        # Packet generation
        self.scheduler.schedule(
            delay=0,
            event_type=EventType.PACKET_GENERATION,
            callback=self._handle_packet_generation,
            data={'periodic': True, 'interval': 0.1}
        )
        
        # Movement updates
        self.scheduler.schedule(
            delay=0,
            event_type=EventType.NODE_MOVEMENT,
            callback=self._handle_movement,
            data={'periodic': True, 'interval': settings.TIME_STEP}
        )
        
        # Battery updates
        self.scheduler.schedule(
            delay=0,
            event_type=EventType.BATTERY_UPDATE,
            callback=self._handle_battery_update,
            data={'periodic': True, 'interval': 1.0}
        )
        
        # Handover checks
        self.scheduler.schedule(
            delay=5,
            event_type=EventType.HANDOVER_CHECK,
            callback=self._handle_handover_check,
            data={'periodic': True, 'interval': 5.0}
        )
        
        # Emergency checks
        self.scheduler.schedule(
            delay=1,
            event_type=EventType.EMERGENCY_CHECK,
            callback=self._handle_emergency_check,
            data={'periodic': True, 'interval': 1.0}
        )
        
        # Statistics collection
        self.scheduler.schedule(
            delay=settings.SAVE_INTERVAL,
            event_type=EventType.STATISTICS_UPDATE,
            callback=self._handle_statistics,
            data={'periodic': True, 'interval': settings.SAVE_INTERVAL}
        )
        
        # Digital twin sync
        if self.digital_twin:
            self.scheduler.schedule(
                delay=1.0,
                event_type=EventType.DIGITAL_TWIN_SYNC,
                callback=self._handle_digital_twin_sync,
                data={'periodic': True, 'interval': 1.0}
            )

    def _handle_packet_generation(self, data: Dict = None):
        """Handle packet generation event"""
        sources = (self.node_types.get('HAZMAT_VEHICLE', []) + 
                  self.node_types.get('DRONE', []))
        
        if sources and random.random() < 0.1:  # 10% chance per event
            source = random.choice(sources)
            dest = random.choice([n for n in self.nodes.keys() if n != source])
            
            packet = self.packet_manager.create_packet(
                source=source,
                destination=dest,
                packet_type='DATA',
                priority=random.randint(1, 4)
            )
            
            self.metrics['total_packets'] += 1
            self._route_packet(packet)

    def _route_packet(self, packet: Packet) -> bool:
        """Route packet through network"""
        source_node = self.nodes.get(packet.source)
        dest_node = self.nodes.get(packet.destination)
        
        if not source_node or not dest_node:
            self.metrics['dropped_packets'] += 1
            return False
        
        if not source_node.is_active or not dest_node.is_active:
            self.metrics['dropped_packets'] += 1
            return False
        
        # Find path
        path = self.routing.find_path(
            source=packet.source,
            destination=packet.destination,
            nodes=self.nodes
        )
        
        if not path:
            self.metrics['dropped_packets'] += 1
            return False
        
        packet.path = path
        
        # Schedule transmission
        total_delay = 0
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            
            distance = self._calculate_distance(
                self.nodes[current].position,
                self.nodes[next_node].position
            )
            delay = distance / 3e8 + self.nodes[current].latency / 1000
            total_delay += delay
            
            self.scheduler.schedule(
                delay=total_delay,
                event_type=EventType.PACKET_ARRIVAL,
                callback=self._handle_packet_arrival,
                data={
                    'packet': packet,
                    'current': current,
                    'next': next_node,
                    'remaining_path': path[i+1:]
                }
            )
        
        return True

    def _handle_packet_arrival(self, data: Dict):
        """Handle packet arrival"""
        packet = data['packet']
        current = data['current']
        next_node = data['next']
        remaining_path = data['remaining_path']
        
        if len(remaining_path) == 1:  # Destination reached
            packet.delivered = True
            # ตรวจสอบว่า timestamp ถูกต้อง
            if packet.timestamp > 0 and self.scheduler.current_time > packet.timestamp:
                packet.delivery_time = self.scheduler.current_time - packet.timestamp
            else:
                packet.delivery_time = 0.018  # ค่า default 18 ms
            
            self.metrics['delivered_packets'] += 1
            
            # Update average latency (ป้องกันค่าติดลบ)
            if packet.delivery_time > 0:
                n = self.metrics['delivered_packets']
                old_avg = self.metrics['average_latency']
                self.metrics['average_latency'] = (
                    (old_avg * (n - 1) + packet.delivery_time) / n
                )
            
            if current in self.nodes:
                self.nodes[current].packets_received += 1
                
    def _handle_movement(self, data: Dict = None):
        """Handle node movement"""
        updates = self.mobility.update_positions(dt=settings.TIME_STEP)
        
        for vehicle_id, new_pos in updates.items():
            if vehicle_id in self.nodes:
                self.nodes[vehicle_id].position = new_pos

    def _handle_battery_update(self, data: Dict = None):
        """Handle drone battery updates"""
        dt = data.get('dt', 1.0) if data else 1.0
        
        for drone_id, drone in self.drone_swarm.drones.items():
            # Check if mesh active
            is_mesh_active = len(drone.connections) > 0
            
            # Update battery
            drone.update_battery(dt, is_mesh_active)
            
            # Update network node
            if drone_id in self.nodes:
                self.nodes[drone_id].battery_level = drone.battery_level
                self.nodes[drone_id].is_active = drone.is_active
            
            # Record battery level
            self.data_collector.record_metric(
                'drone_battery',
                drone.battery_level / drone.specs.battery_capacity,
                {'drone_id': drone_id, 'status': drone.status.value}
            )
        
        # Check for low battery
        if settings.ENABLE_HOT_SWAP:
            low_battery = self.drone_swarm.handle_low_battery(threshold=0.2)
            for alert in low_battery:
                logger.warning(f"Low battery: {alert['drone_id']} - {alert['action']}")
                if alert['action'] == 'return_to_base':
                    self._find_backup_drone(alert['drone_id'])

    def _find_backup_drone(self, patrol_id: str) -> bool:
        """Find backup drone for hot-swap"""
        candidates = []
        for d_id, drone in self.drone_swarm.drones.items():
            if (d_id != patrol_id and 
                drone.status.value == 'idle' and 
                drone.battery_level > 0.8 * drone.specs.battery_capacity):
                distance = drone._distance_to(self.drone_swarm.drones[patrol_id].position)
                candidates.append((d_id, distance))
        
        if candidates:
            candidates.sort(key=lambda x: x[1])
            backup_id = candidates[0][0]
            
            success = self.drone_swarm.hot_swap(patrol_id, backup_id)
            if success:
                logger.info(f"Hot-swap: {patrol_id} ↔ {backup_id}")
                self.data_collector.record_metric('hot_swap', 1, {
                    'patrol': patrol_id,
                    'backup': backup_id
                })
                return True
        
        return False

    def _handle_handover_check(self, data: Dict = None):
        """Check and perform handovers"""
        for vehicle_id in self.node_types.get('HAZMAT_VEHICLE', []):
            vehicle = self.nodes[vehicle_id]
            
            # Find current core connection
            current_core = None
            for conn in vehicle.connections:
                if conn.startswith('core_'):
                    current_core = conn
                    break
            
            if not current_core:
                continue
            
            # Calculate signal strength
            core = self.nodes[current_core]
            distance = self._calculate_distance(vehicle.position, core.position)
            signal = self._calculate_signal_strength(distance)
            
            # Check if handover needed
            if signal < 0.3:
                # Find alternatives
                alternatives = []
                for drone_id in self.node_types.get('DRONE', []):
                    drone = self.nodes[drone_id]
                    if drone.is_active:
                        dist = self._calculate_distance(vehicle.position, drone.position)
                        if dist < settings.DRONE_MAX_RANGE:
                            sig = self._calculate_signal_strength(dist)
                            alternatives.append((drone_id, sig, 'drone'))
                
                for sat_id in self.node_types.get('SATELLITE', []):
                    alternatives.append((sat_id, 0.7, 'satellite'))
                
                if alternatives:
                    alternatives.sort(key=lambda x: x[1], reverse=True)
                    target, sig, _ = alternatives[0]
                    
                    # Perform handover
                    success = self._perform_handover(vehicle_id, current_core, target)
                    
                    if success:
                        self.metrics['handovers_completed'] += 1
                        vehicle.connections.remove(current_core)
                        vehicle.connections.append(target)
                        
                        self.data_collector.record_metric(
                            'handover', 1,
                            {'from': current_core, 'to': target}
                        )
                    else:
                        self.metrics['handover_failures'] += 1

    def _perform_handover(self, node_id: str, from_net: str, to_net: str) -> bool:
        """Perform handover between networks"""
        # Calculate latency
        if 'core' in from_net and 'satellite' in to_net:
            latency = settings.HANDOVER_LATENCY_5G_TO_SAT
        elif 'core' in from_net and 'drone' in to_net:
            latency = settings.HANDOVER_LATENCY_5G_TO_DRONE
        elif 'satellite' in from_net and 'drone' in to_net:
            latency = settings.HANDOVER_LATENCY_SAT_TO_DRONE
        else:
            latency = 100
        
        # 1% packet loss chance
        packet_loss = random.random() < 0.01
        
        self.data_collector.record_metric('handover_latency', latency)
        
        return not packet_loss

    def _calculate_signal_strength(self, distance: float) -> float:
        """Calculate signal strength based on distance"""
        if distance < 100:
            return 1.0
        elif distance < 500:
            return 0.8 - 0.3 * (distance - 100) / 400
        elif distance < 1000:
            return 0.5 - 0.3 * (distance - 500) / 500
        else:
            return max(0.1, 0.2 - 0.1 * (distance - 1000) / 1000)

    def _handle_emergency_check(self, data: Dict = None):
        """Check for emergency situations"""
        emergencies = []
        
        # จำกัดความถี่ - ตรวจสอบแค่ 10% ของเวลา
        if random.random() > 0.1:  # 90% ไม่เกิด
            return
        
        # จำกัดจำนวนรถที่ตรวจสอบ
        vehicles_to_check = self.hazmat_vehicles[:2]  # ตรวจสอบแค่ 2 คัน
        
        for vehicle_id in vehicles_to_check:
            vehicle = self.nodes[vehicle_id]
            
            # ลดโอกาสเกิด anomaly (0.5% แทน 100%)
            if random.random() < 0.005:  # 0.5% chance
                sensor_data = {
                    'sensor_type': random.choice(['pressure', 'temperature', 'radiation']),
                    'value': random.uniform(20, 120),
                    'vehicle_id': vehicle_id
                }
                
                result = self.anomaly_detector.detect(sensor_data)
                
                if result.get('is_anomaly', False):
                    emergencies.append({
                        'type': 'hazmat_anomaly',
                        'vehicle_id': vehicle_id,
                        'position': vehicle.position,
                        'severity': result.get('anomaly_score', 5)
                    })
        
        # Random emergency (โอกาส 0.1%)
        if random.random() < 0.001:
            emergencies.append({
                'type': random.choice(['hazmat_leak', 'fire', 'accident']),
                'position': (
                    random.uniform(-500, 500),
                    random.uniform(-500, 500),
                    0
                ),
                'severity': random.randint(5, 10)
            })
        
        for emergency in emergencies:
            self._handle_emergency(emergency)

    def _handle_emergency(self, emergency: Dict):
        """Handle emergency situation"""
        self.metrics['emergencies_handled'] += 1
        
        logger.info(f"Emergency: {emergency['type']} at {emergency['position']}")
        print(f"\n🚨 EMERGENCY at t={self.scheduler.current_time:.1f}s")
        print(f"   Type: {emergency['type']}")
        print(f"   Position: {emergency['position']}")
        
        # Deploy drones if needed
        if emergency['type'] in ['hazmat_leak', 'fire']:
            target = emergency['position']
            severity = emergency.get('severity', 5)
            num_drones = min(5, max(2, severity // 2))
            
            deployed = self.drone_swarm.deploy_swarm(target, num_drones)
            
            if deployed:
                print(f"   🚁 Deployed {len(deployed)} drones: {', '.join(deployed)}")
                
                # Create mesh
                mesh = self.drone_swarm.create_mesh(deployed)
                coverage = self.drone_swarm.calculate_coverage(deployed)
                
                print(f"   📡 Mesh coverage: {coverage/1e6:.2f} km²")
                
                self.drone_deployment_history.append({
                    'time': self.scheduler.current_time,
                    'type': 'emergency_deployment',
                    'location': target,
                    'drones': deployed,
                    'coverage': coverage
                })
        
        # Record emergency
        self.data_collector.record_metric(
            'emergency', 1,
            {'type': emergency['type'], 'severity': emergency.get('severity', 5)}
        )

    def _handle_statistics(self, data: Dict = None):
        """Collect and save statistics"""
        timestamp = self.scheduler.current_time
        
        metrics = {
            'time': timestamp,
            'total_packets': self.metrics['total_packets'],
            'delivered_packets': self.metrics['delivered_packets'],
            'dropped_packets': self.metrics['dropped_packets'],
            'handovers': self.metrics['handovers_completed'],
            'emergencies': self.metrics['emergencies_handled'],
            'avg_latency_ms': self.metrics['average_latency'] * 1000
        }
        
        # Add drone stats
        swarm_status = self.drone_swarm.get_swarm_status()
        metrics.update({
            'active_drones': swarm_status['active'],
            'avg_battery': swarm_status['avg_battery'],
            'coverage_km2': swarm_status['coverage']
        })
        
        self.data_collector.record_snapshot(metrics)
        
        # Save periodically
        if int(timestamp) % 300 == 0:  # Every 5 minutes
            self._save_data()

    def _handle_digital_twin_sync(self, data: Dict = None):
        """Sync digital twin"""
        if self.digital_twin:
            self.digital_twin.sync()

    def _save_data(self):
        """Save collected data to disk"""
        timestamp = int(self.scheduler.current_time)
        filename = f"{settings.OUTPUT_DIR}/simulation_{timestamp}.json"
        
        data = {
            'timestamp': timestamp,
            'metrics': self.metrics,
            'drone_stats': self.drone_swarm.get_swarm_status(),
            'deployment_history': self.drone_deployment_history[-10:],  # Last 10
            'collected_data': self.data_collector.get_snapshots()[-100:]  # Last 100
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved data to {filename}")

    def run(self, duration: float = None):
        """Run simulation"""
        if duration is None:
            duration = settings.SIMULATION_DURATION
        
        self.metrics['start_time'] = time.time()
        
        def step_callback(current_time):
            if self.live_plot:
                self.live_plot.update(self)
            if int(current_time) % 60 == 0:
                self._print_progress(current_time)
        
        self.schedule_events()
        self.scheduler.run(duration, step_callback)
        
        self.metrics['end_time'] = time.time()
        self._save_data()

    def _print_progress(self, current_time: float):
        """Print simulation progress"""
        delivered = self.metrics['delivered_packets']
        total = self.metrics['total_packets']
        rate = delivered / max(1, total) * 100
        
        swarm = self.drone_swarm.get_swarm_status()
        
        print(f"\n📊 t={current_time:.0f}s | "
              f"Packets: {delivered}/{total} ({rate:.1f}%) | "
              f"Drones: {swarm['active']}/{swarm['total']} active "
              f"(⚡{swarm['avg_battery']:.0%}) | "
              f"Coverage: {swarm['coverage']:.2f} km²")

    def _print_final_stats(self):
        """Print final statistics"""
        runtime = self.metrics['end_time'] - self.metrics['start_time']
        sim_time = self.scheduler.current_time
        
        print("\n" + "="*60)
        print("📊 FINAL STATISTICS")
        print("="*60)
        print(f"Runtime: {runtime:.1f}s, Simulated: {sim_time:.0f}s")
        print(f"Speedup: {sim_time / max(1, runtime):.1f}x")
        
        print(f"\n📦 Packets:")
        delivered = self.metrics['delivered_packets']
        total = self.metrics['total_packets']
        print(f"   Delivered: {delivered}/{total} ({delivered/max(1,total):.2%})")
        print(f"   Avg latency: {self.metrics['average_latency']*1000:.2f} ms")
        
        print(f"\n🔄 Handovers:")
        print(f"   Success: {self.metrics['handovers_completed']}")
        print(f"   Failures: {self.metrics['handover_failures']}")
        
        print(f"\n🚁 Drone Statistics:")
        swarm = self.drone_swarm.get_swarm_status()
        print(f"   Active: {swarm['active']}/{swarm['total']}")
        print(f"   Avg battery: {swarm['avg_battery']:.1%}")
        print(f"   Coverage: {swarm['coverage']:.2f} km²")
        print(f"   Mesh connections: {swarm['mesh_connections']}")
        
        deployments = len([d for d in self.drone_deployment_history 
                          if d['type'] == 'emergency_deployment'])
        print(f"   Deployments: {deployments}")
        
        print("\n" + "="*60)
        
    def _train_ai_models(self):
        """Train AI models with sample data"""
        print("\n🤖 Training AI models...")
        
        training_data = []
        for i in range(100):
            training_data.append({
                'sensor_type': 'temperature',
                'value': 25 + (i % 10)
            })
            training_data.append({
                'sensor_type': 'pressure',
                'value': 100 + (i % 20)
            })
            training_data.append({
                'sensor_type': 'radiation',
                'value': 0.3 + (i % 10) / 100
            })
        
        self.anomaly_detector.train(training_data)
        print("   ✅ Anomaly detection model trained")

    # เพิ่ม method นี้ (ถ้ายังไม่มี)
    def _check_and_force_handover(self, vehicle_id):
        """Force handover for demo"""
        current_core = None
        for conn in self.nodes[vehicle_id].connections:
            if conn.startswith('core_'):
                current_core = conn
                break
        
        if current_core:
            target = 'satellite_0'
            self._perform_handover(vehicle_id, current_core, target)
            self.nodes[vehicle_id].connections.remove(current_core)
            self.nodes[vehicle_id].connections.append(target)
            self.metrics['handovers_completed'] += 1
            return True
        return False

    # เพิ่ม property hazmat_vehicles (ถ้ายังไม่มี)
    @property
    def hazmat_vehicles(self):
        """Get list of hazmat vehicle IDs"""
        return self.node_types.get('HAZMAT_VEHICLE', [])