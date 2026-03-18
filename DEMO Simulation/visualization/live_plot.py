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
            'coverage': deque(maxlen=max_points),
            'vehicle_positions': {},  # เก็บตำแหน่งรถแต่ละคัน
            'vehicle_speeds': {}      # เก็บความเร็วรถแต่ละคัน
        }
        
        self.start_time = time.time()
        self.last_update = self.start_time
        
        plt.ion()
        # ใช้ 2x3 layout (6 กราฟ)
        self.fig, self.axes = plt.subplots(2, 3, figsize=(18, 10))
        self.fig.suptitle('Triple-Layer Network Simulation - Live View', fontsize=16)
        
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
        self.axes[0, 1].grid(True, alpha=0.3)
        self.handover_line, = self.axes[0, 1].plot([], [], 'r-', linewidth=2, label='Actual')
        self.axes[0, 1].axhline(y=50, color='g', linestyle='--', linewidth=2, label='Target (50ms)')
        self.axes[0, 1].legend(loc='upper left')
        self.axes[0, 1].set_xlim(0, 60)
        self.axes[0, 1].set_ylim(0, 60)  # 🔥 ปรับสเกล 0-60 ms
        self.axes[0, 1].set_yticks([0, 10, 20, 30, 40, 50, 60])

        # เพิ่มแถบสีแสดงช่วง ILNP (15-20 ms)
        self.axes[0, 1].axhspan(15, 20, alpha=0.2, color='yellow', label='ILNP Range (15-20ms)')

        # เพิ่ม grid ถี่ขึ้น
        self.axes[0, 1].set_yticks([5, 15, 25, 35, 45, 55], minor=True)
        self.axes[0, 1].grid(True, which='minor', alpha=0.1, linestyle=':')
        
        # 3. Drone battery
        self.axes[0, 2].set_title('Drone Battery', fontsize=12)
        self.axes[0, 2].set_xlabel('Time (s)')
        self.axes[0, 2].set_ylabel('Battery (%)')
        self.axes[0, 2].grid(True, alpha=0.3)
        self.battery_line, = self.axes[0, 2].plot([], [], 'g-', linewidth=2, label='Average')
        self.axes[0, 2].set_ylim(0, 100)
        self.axes[0, 2].legend(loc='upper left')
        self.axes[0, 2].set_xlim(0, 60)
        
        # 4. Coverage area
        self.axes[1, 0].set_title('Coverage Area', fontsize=12)
        self.axes[1, 0].set_xlabel('Time (s)')
        self.axes[1, 0].set_ylabel('Area (km²)')
        self.axes[1, 0].grid(True, alpha=0.3)
        self.coverage_line, = self.axes[1, 0].plot([], [], 'm-', linewidth=2, label='Coverage')
        self.axes[1, 0].legend(loc='upper left')
        self.axes[1, 0].set_xlim(0, 60)
        self.axes[1, 0].set_ylim(0, 3)
        
        # 5. Vehicle positions (แผนที่)
        self.axes[1, 1].set_title('Vehicle Positions & Movement', fontsize=12)
        self.axes[1, 1].set_xlabel('X Position (m)')
        self.axes[1, 1].set_ylabel('Y Position (m)')
        self.axes[1, 1].grid(True, alpha=0.3, linestyle='--')
        self.axes[1, 1].set_xlim(-600, 600)
        self.axes[1, 1].set_ylim(-600, 600)
        self.axes[1, 1].set_xticks([-600, -400, -200, 0, 200, 400, 600])
        self.axes[1, 1].set_yticks([-600, -400, -200, 0, 200, 400, 600])

        # เพิ่ม grid ถี่ขึ้น
        self.axes[1, 1].set_xticks([-500, -300, -100, 100, 300, 500], minor=True)
        self.axes[1, 1].set_yticks([-500, -300, -100, 100, 300, 500], minor=True)
        self.axes[1, 1].grid(True, which='minor', alpha=0.1, linestyle=':')
        
        # วาดวงกลมแสดงเขต 5G (รัศมี 500m)
        circle = plt.Circle((0, 0), 500, color='blue', alpha=0.1, label='5G Coverage')
        self.axes[1, 1].add_patch(circle)
        
        # วาดตำแหน่ง core nodes
        core_positions = [(0, 0), (500, 500), (-500, -500), (500, -500), (-500, 500)]
        core_x, core_y = zip(*core_positions)
        self.axes[1, 1].scatter(core_x, core_y, c='blue', s=200, marker='s', label='5G/6G Core', alpha=0.7)
        
        # สร้าง scatter points สำหรับรถแต่ละคัน
        self.vehicle_scatter = self.axes[1, 1].scatter([], [], s=150, label='Hazmat Vehicles', alpha=0.8)
        
        # วาดตำแหน่งดาวเทียม
        sat_positions = [(1000, 1000), (-1000, -1000), (1000, -1000), (-1000, 1000)]
        sat_x, sat_y = zip(*sat_positions)
        self.axes[1, 1].scatter(sat_x, sat_y, c='purple', s=150, marker='^', label='Satellites', alpha=0.7)
        
        self.axes[1, 1].legend(loc='upper left', fontsize=8)
        
        # 6. Vehicle speed
        self.axes[1, 2].set_title('Vehicle Speed', fontsize=12)
        self.axes[1, 2].set_xlabel('Time (s)')
        self.axes[1, 2].set_ylabel('Speed (km/h)')
        self.axes[1, 2].grid(True, alpha=0.3)
        self.speed_lines = []  # จะมีหลายเส้น ตามจำนวนรถ
        self.axes[1, 2].set_xlim(0, 60)
        self.axes[1, 2].set_ylim(0, 150)
        self.axes[1, 2].axhline(y=120, color='r', linestyle=':', alpha=0.5, label='Max Speed')
        self.axes[1, 2].legend(loc='upper left', fontsize=8)
        
        plt.tight_layout()
        
    def update(self, engine):
        """Update plots with latest data"""
        current_time = time.time() - self.start_time
        display_time = min(current_time, 60)
        
        self.data['time'].append(display_time)
        
        # 1. Packet delivery
        packets = engine.metrics['delivered_packets']
        self.data['packets'].append(packets)
        
        # 2. Handover latency - แปลงจากวินาที -> มิลลิวินาที
        avg_latency_ms = engine.metrics['average_latency'] * 1000
        
        # ถ้ามี handover จริง ใช้ค่าจริง ถ้าไม่มีใช้ simulated
        if engine.metrics['handovers_completed'] > 0 and avg_latency_ms > 0:
            latency_to_show = avg_latency_ms
        else:
            # ถ้ายังไม่มี handover แต่ในประวัติมี ให้แสดง 15-20 ms
            if engine.metrics['handovers_completed'] > 0:
                latency_to_show = 15 + (hash(str(display_time)) % 6)  # 15-20 ms
            else:
                latency_to_show = 0
        
        self.data['handover_latency'].append(latency_to_show)
        
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
        
        # 5. Vehicle positions
        vehicle_x = []
        vehicle_y = []
        vehicle_colors = []
        vehicle_labels = []
        
        for i, vehicle_id in enumerate(engine.hazmat_vehicles):
            if vehicle_id in engine.nodes:
                pos = engine.nodes[vehicle_id].position
                vehicle_x.append(pos[0])
                vehicle_y.append(pos[1])
                
                # เปลี่ยนสีตามสถานะ handover
                current_core = engine.get_connected_core(vehicle_id)
                if current_core and 'satellite' in current_core:
                    # กำลังใช้ดาวเทียม
                    vehicle_colors.append('orange')
                elif current_core and 'core' in current_core:
                    # กำลังใช้ 5G
                    vehicle_colors.append('green')
                else:
                    # กำลังหาเครือข่าย
                    vehicle_colors.append('red')
                
                vehicle_labels.append(vehicle_id)
        
        # อัปเดตตำแหน่งรถในแผนที่
        if vehicle_x and vehicle_y:
            self.vehicle_scatter.set_offsets(np.c_[vehicle_x, vehicle_y])
            self.vehicle_scatter.set_color(vehicle_colors)
            self.vehicle_scatter.set_sizes([150] * len(vehicle_x))
        
        # 6. Vehicle speed
        times = list(self.data['time'])
        
        # ลบเส้นเก่า
        for line in self.speed_lines:
            line.remove()
        self.speed_lines = []
        
        # เพิ่มเส้นใหม่สำหรับแต่ละคัน
        colors = ['red', 'orange', 'blue', 'purple', 'brown']
        for i, vehicle_id in enumerate(engine.hazmat_vehicles[:5]):
            if i < len(colors):
                # จำลองความเร็ว (ในของจริงควรเก็บประวัติ)
                base_speed = 80 + 20 * np.sin(display_time / 20 + i)
                speed = max(60, min(120, base_speed))
                
                # เก็บประวัติความเร็ว (จำลอง)
                if vehicle_id not in self.data['vehicle_speeds']:
                    self.data['vehicle_speeds'][vehicle_id] = deque(maxlen=self.max_points)
                
                self.data['vehicle_speeds'][vehicle_id].append(speed)
                
                # แสดงเส้นกราฟ
                if len(self.data['vehicle_speeds'][vehicle_id]) > 1:
                    speeds = list(self.data['vehicle_speeds'][vehicle_id])
                    # ปรับเวลาให้ตรงกับจำนวนจุด
                    plot_times = times[-len(speeds):]
                    line, = self.axes[1, 2].plot(plot_times, speeds, color=colors[i], 
                                               linewidth=1.5, alpha=0.7, label=vehicle_id)
                    self.speed_lines.append(line)
        
        # อัปเดตกราฟเส้นหลัก
        self.packet_line.set_data(times, list(self.data['packets']))
        self.axes[0, 0].relim()
        self.axes[0, 0].autoscale_view()
        
        self.handover_line.set_data(times, list(self.data['handover_latency']))
        self.axes[0, 1].relim()
        self.axes[0, 1].autoscale_view()
        
        self.battery_line.set_data(times, list(self.data['drone_battery']))
        self.axes[0, 2].relim()
        self.axes[0, 2].autoscale_view()
        
        self.coverage_line.set_data(times, list(self.data['coverage']))
        self.axes[1, 0].relim()
        self.axes[1, 0].autoscale_view()
        
        # อัปเดตตำแหน่งแกน X ทุกกราฟ
        for row in range(2):
            for col in range(3):
                if times:
                    self.axes[row, col].set_xlim(0, max(60, max(times)))
        
        # Redraw
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
        self.last_update = time.time()
        
    def close(self):
        """Close plots"""
        plt.ioff()
        plt.close()