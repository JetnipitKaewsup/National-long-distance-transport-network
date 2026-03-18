"""
Dashboard for displaying simulation status
"""
import time
from typing import Dict, Any

class Dashboard:
    """Text-based dashboard for simulation monitoring"""
    
    def __init__(self, refresh_rate: float = 1.0):
        self.refresh_rate = refresh_rate
        self.last_update = 0
        self.stats = {}
        
    def clear_screen(self):
        """Clear terminal screen"""
        print('\033[2J\033[H', end='')
        
    def format_progress_bar(self, value: float, max_val: float, 
                           width: int = 20) -> str:
        """Create progress bar"""
        percent = value / max_val
        filled = int(width * percent)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percent:.1%}"
    
    def update(self, engine):
        """Update dashboard display"""
        current_time = time.time()
        
        if current_time - self.last_update < self.refresh_rate:
            return
        
        self.clear_screen()
        
        # Header
        print("="*60)
        print("🚁 TRIPLE-LAYER NETWORK SIMULATION DASHBOARD")
        print("="*60)
        print(f"Time: {engine.scheduler.current_time:.1f}s / {engine.scheduler.current_time:.0f}s")
        print("-"*60)
        
        # Network stats
        print("\n📡 NETWORK STATUS")
        delivered = engine.metrics['delivered_packets']
        total = engine.metrics['total_packets']
        rate = delivered / max(1, total) * 100
        
        print(f"  Packets: {delivered}/{total} ({rate:.1f}%)")
        print(f"  Avg Latency: {engine.metrics['average_latency']*1000:.2f} ms")
        print(f"  Handovers: {engine.metrics['handovers_completed']} "
              f"(fail: {engine.metrics['handover_failures']})")
        
        # Drone stats
        print("\n🚁 DRONE STATUS")
        swarm = engine.drone_swarm.get_swarm_status()
        print(f"  Active: {swarm['active']}/{swarm['total']}")
        print(f"  Battery: {self.format_progress_bar(swarm['avg_battery'], 1.0)}")
        print(f"  Coverage: {swarm['coverage']:.2f} km²")
        print(f"  Mesh Connections: {swarm['mesh_connections']}")
        
        # Individual drone status
        print("\n  Individual Drones:")
        for drone_id, drone in list(engine.drone_swarm.drones.items())[:5]:
            battery = drone.battery_level / drone.specs.battery_capacity
            bar = self.format_progress_bar(battery, 1.0, 10)
            print(f"    {drone_id}: {bar} [{drone.status.value}]")
        
        # Emergency stats
        print("\n🚨 EMERGENCY STATUS")
        print(f"  Emergencies Handled: {engine.metrics['emergencies_handled']}")
        
        if engine.drone_deployment_history:
            last = engine.drone_deployment_history[-1]
            print(f"  Last Deployment: {last['type']} at t={last['time']:.1f}s")
        
        # Footer
        print("\n" + "="*60)
        print(f"Press Ctrl+C to stop simulation")
        
        self.last_update = current_time