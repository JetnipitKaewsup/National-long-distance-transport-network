"""
Network constants for the simulation
"""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class NetworkConstants:
    """Central configuration for network parameters"""

    # 5G/6G Core Parameters
    CORE_BANDWIDTH_5G: float = 10 * 1024  # 10 Gbps
    CORE_BANDWIDTH_6G: float = 100 * 1024  # 100 Gbps
    CORE_LATENCY_5G: float = 1  # 1 ms
    CORE_LATENCY_6G: float = 0.1  # 0.1 ms
    CORE_RELIABILITY_5G: float = 0.999
    CORE_RELIABILITY_6G: float = 0.9999

    # Satellite Parameters
    SAT_BANDWIDTH: float = 100  # 100 Mbps
    SAT_LATENCY: float = 250  # 250 ms
    SAT_RELIABILITY: float = 0.95

    # Drone Mesh Parameters
    DRONE_BANDWIDTH: float = 50  # 50 Mbps
    DRONE_LATENCY: float = 10  # 10 ms per hop
    DRONE_RELIABILITY: float = 0.9
    DRONE_BATTERY_CAPACITY: float = 3600  # 1 hour in seconds
    DRONE_CHARGE_RATE: float = 600  # 10% per minute
    DRONE_MAX_RANGE: float = 1000  # meters
    DRONE_SPEED: float = 15  # meters per second
    DRONE_MESH_RANGE: float = 300  # meters for drone-to-drone

    # Handover Parameters
    HANDOVER_LATENCY_5G_TO_SAT: float = 500  # 500 ms
    HANDOVER_LATENCY_5G_TO_DRONE: float = 100  # 100 ms
    HANDOVER_LATENCY_SAT_TO_DRONE: float = 200  # 200 ms

    # Emergency Priorities
    PRIORITY_LEVELS: Dict[str, int] = field(default_factory=lambda: {
        'critical': 1,
        'high': 2,
        'medium': 3,
        'low': 4
    })

    # Simulation Parameters
    SIMULATION_DURATION: float = 3600  # 1 hour
    UPDATE_INTERVAL: float = 0.1  # 100 ms
    PACKET_GENERATION_RATE: float = 10  # packets per second per node

# Create global instance
CONSTANTS = NetworkConstants()