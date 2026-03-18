"""
Digital Twin for network state synchronization and prediction
"""
import time
from typing import Dict, List, Any

class DigitalTwin:
    """Digital Twin representation of physical network"""
    
    def __init__(self, network_simulator):
        self.physical_network = network_simulator
        self.state_history = []
        self.sync_interval = 1.0
        self.last_sync = time.time()
        
    def sync(self):
        """Sync with physical network"""
        current_state = {
            'timestamp': time.time(),
            'nodes': self._capture_nodes_state(),
            'links': self._capture_links_state()
        }
        self.state_history.append(current_state)
        self.last_sync = current_state['timestamp']
        
        if len(self.state_history) > 100:
            self.state_history.pop(0)
    
    def _capture_nodes_state(self) -> Dict:
        """Capture state of all nodes"""
        nodes_state = {}
        for node_id, node in self.physical_network.nodes.items():
            nodes_state[node_id] = {
                'type': node.node_type,
                'position': node.position,
                'active': node.is_active,
                'battery': node.battery_level,
                'connections': len(node.connections)
            }
        return nodes_state
    
    def _capture_links_state(self) -> Dict:
        """Capture state of all links"""
        links = {}
        for node_id, node in self.physical_network.nodes.items():
            for conn_id in node.connections[:5]:
                if conn_id in self.physical_network.nodes:
                    link_key = f"{node_id}-{conn_id}"
                    links[link_key] = {
                        'active': node.is_active and self.physical_network.nodes[conn_id].is_active
                    }
        return links
    
    def predict_node_failure(self, node_id: str) -> float:
        """Predict probability of node failure"""
        node = self.physical_network.nodes.get(node_id)
        if not node or not node.is_active:
            return 1.0
            
        failure_prob = 0.0
        
        # Battery based prediction
        if node.node_type == 'DRONE' and node.battery_level:
            battery_ratio = node.battery_level / 3600
            if battery_ratio < 0.2:
                failure_prob += 0.7
            elif battery_ratio < 0.4:
                failure_prob += 0.3
        
        return min(failure_prob, 1.0)