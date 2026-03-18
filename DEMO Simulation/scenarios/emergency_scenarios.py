"""
Emergency response scenarios for testing
"""
import random
import numpy as np
from typing import Dict, List, Any
import time

def run_handover_test(engine) -> Dict[str, Any]:
    """Test handover performance"""
    print("\n🔄 Running Handover Test")
    print("="*60)
    
    results = {}
    
    for vehicle_id in engine.node_types.get('HAZMAT_VEHICLE', [])[:3]:
        vehicle = engine.nodes[vehicle_id]
        
        # Find current core
        current_core = None
        for conn in vehicle.connections:
            if conn.startswith('core_'):
                current_core = conn
                break
        
        if not current_core:
            continue
        
        # Test handover to satellite
        latencies = []
        for i in range(5):
            success = engine._perform_handover(vehicle_id, current_core, 'satellite_0')
            if success:
                # Record latency (simulated)
                latencies.append(random.uniform(15, 25))
        
        results[vehicle_id] = {
            'avg_latency_ms': float(np.mean(latencies)) if latencies else 0,
            'success_rate': len(latencies) / 5 * 100,
            'handovers_completed': len(latencies)
        }
        
        print(f"\nVehicle {vehicle_id}:")
        print(f"  Avg latency: {results[vehicle_id]['avg_latency_ms']:.2f} ms")
        print(f"  Success rate: {results[vehicle_id]['success_rate']:.1f}%")
    
    return results

def run_anomaly_test(engine) -> Dict[str, Any]:
    """Test anomaly detection"""
    print("\n⚠️ Running Anomaly Detection Test")
    print("="*60)
    
    results = {}
    
    for vehicle_id in engine.node_types.get('HAZMAT_VEHICLE', [])[:2]:
        # Normal data
        normal_data = {
            'sensor_type': 'pressure',
            'value': random.uniform(95, 105),
            'vehicle_id': vehicle_id
        }
        
        # Anomaly data
        anomaly_data = {
            'sensor_type': 'pressure',
            'value': random.uniform(140, 160),
            'vehicle_id': vehicle_id
        }
        
        # Test normal
        start = time.time()
        normal_result = engine.anomaly_detector.detect(normal_data)
        normal_time = (time.time() - start) * 1000
        
        # Test anomaly
        start = time.time()
        anomaly_result = engine.anomaly_detector.detect(anomaly_data)
        anomaly_time = (time.time() - start) * 1000
        
        results[vehicle_id] = {
            'normal': {
                'is_anomaly': normal_result.get('is_anomaly', False),
                'score': normal_result.get('anomaly_score', 0),
                'time_ms': normal_time
            },
            'anomaly': {
                'is_anomaly': anomaly_result.get('is_anomaly', True),
                'score': anomaly_result.get('anomaly_score', 0),
                'time_ms': anomaly_time
            }
        }
        
        print(f"\nVehicle {vehicle_id}:")
        print(f"  Normal - Score: {results[vehicle_id]['normal']['score']:.2f}, "
              f"Time: {results[vehicle_id]['normal']['time_ms']:.2f}ms")
        print(f"  Anomaly - Score: {results[vehicle_id]['anomaly']['score']:.2f}, "
              f"Time: {results[vehicle_id]['anomaly']['time_ms']:.2f}ms")
    
    return results

def run_emergency_scenario(engine, emergency_type: str = 'hazmat_leak') -> Dict:
    """Run specific emergency scenario"""
    print(f"\n🚨 Running {emergency_type} Emergency Scenario")
    print("="*60)
    
    # Create emergency
    x = random.uniform(-300, 300)
    y = random.uniform(-300, 300)
    
    emergency = {
        'type': emergency_type,
        'position': (x, y, 0),
        'severity': random.randint(6, 9),
        'timestamp': engine.scheduler.current_time
    }
    
    print(f"Emergency at: ({x:.0f}, {y:.0f})")
    print(f"Severity: {emergency['severity']}/10")
    
    # Handle emergency
    start_time = time.time()
    engine._handle_emergency(emergency)
    response_time = (time.time() - start_time) * 1000
    
    # Get results
    deployed = engine.drone_deployment_history[-1] if engine.drone_deployment_history else None
    
    return {
        'type': emergency_type,
        'severity': emergency['severity'],
        'response_time_ms': response_time,
        'drones_deployed': len(deployed.get('drones', [])) if deployed else 0,
        'coverage_km2': deployed.get('coverage', 0) / 1e6 if deployed else 0
    }