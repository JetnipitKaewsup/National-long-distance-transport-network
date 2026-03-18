"""
Data analysis for simulation results
"""
import numpy as np
from typing import Dict, List, Any, Optional
from collections import defaultdict
import json
import os

class DataAnalyzer:
    """Analyze simulation data"""
    
    def __init__(self, data_dir: str = './simulation_output'):
        self.data_dir = data_dir
        self.results = {}
        
    def load_simulation_data(self, filename: str) -> Dict:
        """Load simulation data from JSON file"""
        with open(filename, 'r') as f:
            return json.load(f)
    
    def analyze_handover_performance(self, data: Dict) -> Dict:
        """Analyze handover performance metrics"""
        latencies = []
        for metric in data.get('metrics', {}).get('handover_latency', []):
            if isinstance(metric, dict):
                latencies.append(metric.get('value', 0))
        
        if not latencies:
            return {}
        
        return {
            'avg_latency_ms': float(np.mean(latencies)),
            'p95_latency_ms': float(np.percentile(latencies, 95)),
            'p99_latency_ms': float(np.percentile(latencies, 99)),
            'max_latency_ms': float(np.max(latencies)),
            'min_latency_ms': float(np.min(latencies)),
            'std_latency_ms': float(np.std(latencies)),
            'total_handovers': len(latencies)
        }
    
    def analyze_packet_delivery(self, data: Dict) -> Dict:
        """Analyze packet delivery metrics"""
        metrics = data.get('metrics', {})
        total = metrics.get('total_packets', [])
        delivered = metrics.get('delivered_packets', [])
        dropped = metrics.get('dropped_packets', [])
        
        if not total:
            return {}
        
        latest_total = total[-1].get('value', 0) if total else 0
        latest_delivered = delivered[-1].get('value', 0) if delivered else 0
        latest_dropped = dropped[-1].get('value', 0) if dropped else 0
        
        delivery_rate = latest_delivered / max(1, latest_total) * 100
        
        return {
            'total_packets': latest_total,
            'delivered': latest_delivered,
            'dropped': latest_dropped,
            'delivery_rate': delivery_rate,
            'packets_per_second': latest_total / max(1, data.get('timestamp', 1))
        }
    
    def analyze_drone_performance(self, data: Dict) -> Dict:
        """Analyze drone performance metrics"""
        drone_batteries = data.get('metrics', {}).get('drone_battery', [])
        hot_swaps = data.get('metrics', {}).get('hot_swap', [])
        
        if not drone_batteries:
            return {}
        
        # Battery analysis
        battery_values = [m.get('value', 0) for m in drone_batteries]
        
        # Group by drone
        drone_batteries_by_id = defaultdict(list)
        for m in drone_batteries:
            tags = m.get('tags', {})
            drone_id = tags.get('drone_id', 'unknown')
            drone_batteries_by_id[drone_id].append(m.get('value', 0))
        
        avg_battery_by_drone = {
            drone_id: float(np.mean(values))
            for drone_id, values in drone_batteries_by_id.items()
        }
        
        return {
            'avg_battery': float(np.mean(battery_values)),
            'min_battery': float(np.min(battery_values)),
            'max_battery': float(np.max(battery_values)),
            'avg_battery_by_drone': avg_battery_by_drone,
            'hot_swaps_performed': len(hot_swaps),
            'active_drones': len(drone_batteries_by_id)
        }
    
    def analyze_emergency_response(self, data: Dict) -> Dict:
        """Analyze emergency response metrics"""
        emergencies = data.get('metrics', {}).get('emergency', [])
        
        if not emergencies:
            return {}
        
        severity_by_type = defaultdict(list)
        for e in emergencies:
            tags = e.get('tags', {})
            e_type = tags.get('type', 'unknown')
            severity = tags.get('severity', 5)
            severity_by_type[e_type].append(severity)
        
        return {
            'total_emergencies': len(emergencies),
            'by_type': {
                e_type: {
                    'count': len(severities),
                    'avg_severity': float(np.mean(severities))
                }
                for e_type, severities in severity_by_type.items()
            }
        }
    
    def analyze_coverage(self, data: Dict) -> Dict:
        """Analyze coverage metrics"""
        # Get drone deployment history
        deployments = data.get('deployment_history', [])
        
        if not deployments:
            return {}
        
        coverages = [d.get('coverage', 0) for d in deployments if 'coverage' in d]
        
        return {
            'avg_coverage_km2': float(np.mean(coverages)) / 1e6 if coverages else 0,
            'max_coverage_km2': float(np.max(coverages)) / 1e6 if coverages else 0,
            'total_deployments': len(deployments)
        }
    
    def analyze_all(self, filename: str) -> Dict:
        """Run all analyses on a simulation file"""
        data = self.load_simulation_data(filename)
        
        results = {
            'handover': self.analyze_handover_performance(data),
            'packet': self.analyze_packet_delivery(data),
            'drone': self.analyze_drone_performance(data),
            'emergency': self.analyze_emergency_response(data),
            'coverage': self.analyze_coverage(data)
        }
        
        self.results[filename] = results
        return results
    
    def compare_simulations(self, filenames: List[str]) -> Dict:
        """Compare multiple simulation runs"""
        comparison = {}
        
        for fname in filenames:
            if fname not in self.results:
                self.analyze_all(fname)
            comparison[fname] = self.results[fname]
        
        # Calculate statistics across runs
        if len(filenames) > 1:
            delivery_rates = []
            handover_latencies = []
            
            for fname in filenames:
                if 'packet' in self.results[fname]:
                    delivery_rates.append(self.results[fname]['packet'].get('delivery_rate', 0))
                if 'handover' in self.results[fname]:
                    handover_latencies.append(self.results[fname]['handover'].get('avg_latency_ms', 0))
            
            comparison['summary'] = {
                'avg_delivery_rate': float(np.mean(delivery_rates)),
                'std_delivery_rate': float(np.std(delivery_rates)),
                'avg_handover_latency': float(np.mean(handover_latencies)),
                'std_handover_latency': float(np.std(handover_latencies))
            }
        
        return comparison
    
    def generate_report(self, filename: str, output_file: str = None):
        """Generate human-readable report"""
        if filename not in self.results:
            self.analyze_all(filename)
        
        results = self.results[filename]
        
        report = []
        report.append("="*60)
        report.append("SIMULATION ANALYSIS REPORT")
        report.append("="*60)
        report.append(f"File: {filename}")
        report.append("")
        
        # Packet statistics
        if results['packet']:
            p = results['packet']
            report.append("📦 PACKET STATISTICS")
            report.append("-"*40)
            report.append(f"  Total packets: {p.get('total_packets', 0)}")
            report.append(f"  Delivered: {p.get('delivered', 0)}")
            report.append(f"  Dropped: {p.get('dropped', 0)}")
            report.append(f"  Delivery rate: {p.get('delivery_rate', 0):.2f}%")
            report.append(f"  Packets/sec: {p.get('packets_per_second', 0):.2f}")
            report.append("")
        
        # Handover statistics
        if results['handover']:
            h = results['handover']
            report.append("🔄 HANDOVER STATISTICS")
            report.append("-"*40)
            report.append(f"  Total handovers: {h.get('total_handovers', 0)}")
            report.append(f"  Average latency: {h.get('avg_latency_ms', 0):.2f} ms")
            report.append(f"  P95 latency: {h.get('p95_latency_ms', 0):.2f} ms")
            report.append(f"  P99 latency: {h.get('p99_latency_ms', 0):.2f} ms")
            report.append(f"  Max latency: {h.get('max_latency_ms', 0):.2f} ms")
            report.append("")
        
        # Drone statistics
        if results['drone']:
            d = results['drone']
            report.append("🚁 DRONE STATISTICS")
            report.append("-"*40)
            report.append(f"  Active drones: {d.get('active_drones', 0)}")
            report.append(f"  Average battery: {d.get('avg_battery', 0):.1%}")
            report.append(f"  Hot-swaps performed: {d.get('hot_swaps_performed', 0)}")
            report.append("")
        
        # Emergency statistics
        if results['emergency']:
            e = results['emergency']
            report.append("🚨 EMERGENCY STATISTICS")
            report.append("-"*40)
            report.append(f"  Total emergencies: {e.get('total_emergencies', 0)}")
            for e_type, stats in e.get('by_type', {}).items():
                report.append(f"  • {e_type}: {stats['count']} (severity {stats['avg_severity']:.1f})")
            report.append("")
        
        # Coverage statistics
        if results['coverage']:
            c = results['coverage']
            report.append("📡 COVERAGE STATISTICS")
            report.append("-"*40)
            report.append(f"  Average coverage: {c.get('avg_coverage_km2', 0):.2f} km²")
            report.append(f"  Max coverage: {c.get('max_coverage_km2', 0):.2f} km²")
            report.append(f"  Total deployments: {c.get('total_deployments', 0)}")
        
        report.append("="*60)
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
        
        return report_text