"""
Packet management for network simulation
"""
import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class PacketType(Enum):
    """Types of network packets"""
    DATA = "data"
    CONTROL = "control"
    EMERGENCY = "emergency"
    TELEMETRY = "telemetry"

@dataclass
class Packet:
    """Network packet"""
    id: str
    source: str
    destination: str
    packet_type: PacketType
    priority: int
    size: int = 1024  # bytes
    data: Any = None
    timestamp: float = field(default_factory=time.time)
    path: List[str] = field(default_factory=list)
    delivered: bool = False
    delivery_time: float = None
    
    def __lt__(self, other):
        return self.priority < other.priority

class PacketManager:
    """Manage packet generation and handling"""
    
    def __init__(self):
        self.packets: List[Packet] = []
        self.packet_count = 0
        self.packet_history: Dict[str, List[Packet]] = {}
        
    def create_packet(self, source: str, destination: str, 
                     packet_type: str = 'DATA',
                     priority: int = 3,
                     data: Any = None,
                     size: int = None) -> Packet:
        """Create a new packet"""
        packet_id = f"pkt_{self.packet_count}_{time.time()}"
        
        if size is None:
            size = random.randint(64, 1500)  # 64-1500 bytes
        
        packet = Packet(
            id=packet_id,
            source=source,
            destination=destination,
            packet_type=PacketType(packet_type.lower()),
            priority=priority,
            size=size,
            data=data,
            timestamp=time.time()
        )
        
        self.packets.append(packet)
        self.packet_count += 1
        
        # Store in history
        if source not in self.packet_history:
            self.packet_history[source] = []
        self.packet_history[source].append(packet)
        
        return packet
    
    def get_packet(self, packet_id: str) -> Optional[Packet]:
        """Get packet by ID"""
        for packet in self.packets:
            if packet.id == packet_id:
                return packet
        return None
    
    def get_pending_packets(self) -> List[Packet]:
        """Get undelivered packets"""
        return [p for p in self.packets if not p.delivered]
    
    def get_queue_size(self, node_id: str) -> int:
        """Get queue size for node"""
        return len([p for p in self.packets 
                   if not p.delivered and p.source == node_id])
    
    def get_stats(self) -> Dict:
        """Get packet statistics"""
        total = len(self.packets)
        delivered = len([p for p in self.packets if p.delivered])
        by_type = {}
        
        for p in self.packets:
            t = p.packet_type.value
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            'total': total,
            'delivered': delivered,
            'pending': total - delivered,
            'by_type': by_type
        }