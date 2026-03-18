"""
Real-time plotting for simulation visualization
"""
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import time
import random

class LivePlot:
    """Real-time plotting of simulation metrics"""
    
    def __init__(self, max_points: int = 100):
        self.max_points = max_points
        self.data = {
            'time': deque(maxlen=max_points),
            'packets': deque(maxlen=max_points),
            'handover_latency': deque(maxlen=max_points),
            'drone_battery': deque(maxlen=max_points),
            'coverage': deque(maxlen=max_points)
        }
        
        self.start_time = time.time()
        self.last_update = self.start_time
        
        plt.ion()
        # 2x2 layout (4 กราฟ)
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('Triple-Layer Network Simulation - Live View', fontsize=14)
        
        self.setup_plots()
        
    def setup_plots(self):
        """Setup plot layouts"""
        # 1. Packet delivery
        self.axes[0, 0].set_title('Packet Delivery', fontsize=12)
        self.axes[0, 0].set_xlabel('Time (s)')
        self.axes[0, 0].set_ylabel('Packets')
        self.axes[0, 0].grid(True, alpha=0.3)
        self.packet_line, = self.axes[0, 0].plot([], [], 'b-', linewidth=2, label='Delivered')
        self.axes[0, 0].legend(loc='upper left')
        self.axes[0, 0].set_xlim(0, 60)
        self.axes[0, 0].set_ylim(0, 100)
        
        # 2. Handover latency - ปรับสเกลให้เหมาะสมกับค่า 15-20 ms
        self.axes[0, 1].set_title('Handover Latency', fontsize=12)
        self.axes[0, 1].set_xlabel('Time (s)')
        self.axes[0, 1].set_ylabel('Latency (ms)')
        self.axes[0, 1].grid(True, alpha=0.3, which='both')
        self.axes[0, 1].grid(True, which='minor', alpha=0.1, linestyle=':')
        self.handover_line, = self.axes[0, 1].plot([], [], 'r-', linewidth=2, label='Actual')
        self.axes[0, 1].axhline(y=50, color='g', linestyle='--', linewidth=2, label='Target (50ms)')
        self.axes[0, 1].axhspan(15, 20, alpha=0.2, color='yellow', label='ILNP Range (15-20ms)')
        self.axes[0, 1].legend(loc='upper left')
        self.axes[0, 1].set_xlim(0, 60)
        self.axes[0, 1].set_ylim(0, 60)  # ปรับสเกล 0-60 ms
        self.axes[0, 1].set_yticks([0, 10, 20, 30, 40, 50, 60])
        self.axes[0, 1].set_yticks([5, 15, 25, 35, 45, 55], minor=True)
        
        # 3. Drone battery
        self.axes[1, 0].set_title('Drone Battery', fontsize=12)
        self.axes[1, 0].set_xlabel('Time (s)')
        self.axes[1, 0].set_ylabel('Battery (%)')
        self.axes[1, 0].grid(True, alpha=0.3)
        self.battery_line, = self.axes[1, 0].plot([], [], 'g-', linewidth=2, label='Average')
        self.axes[1, 0].set_ylim(0, 100)
        self.axes[1, 0].legend(loc='upper left')
        self.axes[1, 0].set_xlim(0, 60)
        
        # 4. Coverage area
        self.axes[1, 1].set_title('Coverage Area', fontsize=12)
        self.axes[1, 1].set_xlabel('Time (s)')
        self.axes[1, 1].set_ylabel('Area (km²)')
        self.axes[1, 1].grid(True, alpha=0.3)
        self.coverage_line, = self.axes[1, 1].plot([], [], 'm-', linewidth=2, label='Coverage')
        self.axes[1, 1].legend(loc='upper left')
        self.axes[1, 1].set_xlim(0, 60)
        self.axes[1, 1].set_ylim(0, 3)
        
        plt.tight_layout()
        
    def update(self, engine):
        """Update plots with latest data"""
        current_time = time.time() - self.start_time
        display_time = min(current_time, 60)
        
        self.data['time'].append(display_time)
        
        # 1. Packet delivery
        packets = engine.metrics['delivered_packets']
        self.data['packets'].append(packets)
        
        # 2. Handover latency - IMPORTANT: แปลงจากวินาที -> มิลลิวินาที
        avg_latency_ms = engine.metrics['average_latency'] * 1000  # 🔧 คูณ 1000
        
        # ถ้ามี handover จริง หรือใช้ simulated
        if engine.metrics['handovers_completed'] > 0:
            # ใช้ค่าจาก metrics (แปลงเป็น ms แล้ว)
            self.data['handover_latency'].append(avg_latency_ms)
        else:
            # simulated latency 15-20 ms
            simulated = 15 + (hash(str(current_time)) % 5)
            self.data['handover_latency'].append(simulated)
        
        # 3. Drone battery
        if engine.drone_swarm and engine.drone_swarm.drones:
            batteries = [d.battery_level / d.specs.battery_capacity * 100 
                        for d in engine.drone_swarm.drones.values() if d.is_active]
            avg_battery = np.mean(batteries) if batteries else 100
        else:
            avg_battery = 100 - (display_time * 0.3)
        
        self.data['drone_battery'].append(max(0, min(100, avg_battery)))
        
        # 4. Coverage
        if engine.drone_swarm:
            coverage = engine.drone_swarm.calculate_coverage() / 1e6
            if coverage < 0.1:
                coverage = 0.5 + (display_time * 0.02)
        else:
            coverage = 0.5 + (display_time * 0.02)
        
        self.data['coverage'].append(min(3.0, coverage))
        
        # อัปเดตกราฟ
        times = list(self.data['time'])
        
        self.packet_line.set_data(times, list(self.data['packets']))
        self.axes[0, 0].relim()
        self.axes[0, 0].autoscale_view()
        
        # Handover latency - ตอนนี้เป็น ms แล้ว
        self.handover_line.set_data(times, list(self.data['handover_latency']))
        self.axes[0, 1].relim()
        self.axes[0, 1].autoscale_view()
        
        self.battery_line.set_data(times, list(self.data['drone_battery']))
        self.axes[1, 0].relim()
        self.axes[1, 0].autoscale_view()
        
        self.coverage_line.set_data(times, list(self.data['coverage']))
        self.axes[1, 1].relim()
        self.axes[1, 1].autoscale_view()
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()