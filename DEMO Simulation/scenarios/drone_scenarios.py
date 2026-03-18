"""
Drone-specific scenarios for testing
"""
import numpy as np
from typing import Dict, List

def run_drone_coverage_test(engine, duration: float = 300) -> Dict:
    """Test drone coverage over time"""
    print("\n🚁 Running Drone Coverage Test")
    print("="*60)
    
    initial = engine.drone_swarm.calculate_coverage()
    print(f"Initial coverage: {initial/1e6:.2f} km²")
    
    engine.scheduler.run(duration)
    
    final = engine.drone_swarm.calculate_coverage()
    print(f"Final coverage: {final/1e6:.2f} km²")
    print(f"Change: {(final - initial)/1e6:+.2f} km²")
    
    return {
        'initial_km2': initial / 1e6,
        'final_km2': final / 1e6,
        'change_km2': (final - initial) / 1e6
    }

def run_battery_management_test(engine) -> List[Dict]:
    """Test battery management and hot-swap"""
    print("\n🔋 Running Battery Management Test")
    print("="*60)
    
    alerts = engine.drone_swarm.handle_low_battery(threshold=0.3)
    
    for alert in alerts:
        print(f"Alert: {alert['drone_id']} - {alert['action']}")
        
        if alert['action'] == 'return_to_base':
            # Find backup
            for d_id, drone in engine.drone_swarm.drones.items():
                if (d_id != alert['drone_id'] and 
                    drone.status.value == 'idle' and
                    drone.battery_level > 0.8 * drone.specs.battery_capacity):
                    backup = d_id
                    break
            else:
                backup = None
            
            if backup:
                success = engine.drone_swarm.hot_swap(alert['drone_id'], backup)
                print(f"Hot-swap {'successful' if success else 'failed'}")
                alert['backup'] = backup
                alert['hot_swap_success'] = success
    
    return alerts

def run_mesh_communication_test(engine) -> Dict:
    """Test mesh communication between drones"""
    print("\n📡 Running Mesh Communication Test")
    print("="*60)
    
    active = [d_id for d_id, d in engine.drone_swarm.drones.items() if d.is_active]
    
    if len(active) < 2:
        return {'error': 'Not enough active drones'}
    
    mesh = engine.drone_swarm.create_mesh(active)
    print(f"Mesh created with {len(mesh)} nodes")
    
    routes = []
    for i in range(min(3, len(active))):
        for j in range(i+1, min(3, len(active))):
            path = engine.drone_swarm.find_route(active[i], active[j])
            if path:
                routes.append({
                    'source': active[i],
                    'destination': active[j],
                    'path': path,
                    'hops': len(path) - 1
                })
                print(f"Route {active[i]} → {active[j]}: {len(path)-1} hops")
    
    coverage = engine.drone_swarm.calculate_coverage(active)
    
    return {
        'mesh_nodes': len(mesh),
        'routes_found': len(routes),
        'routes': routes,
        'coverage_km2': coverage / 1e6
    }

def run_emergency_deployment_test(engine) -> Dict:
    """Test emergency drone deployment"""
    print("\n🚨 Running Emergency Deployment Test")
    print("="*60)
    
    import random
    x = random.uniform(-500, 500)
    y = random.uniform(-500, 500)
    target = (x, y, 100)
    
    print(f"Emergency at: ({x:.0f}, {y:.0f})")
    
    deployed = engine.drone_swarm.deploy_swarm(target, num_drones=3)
    
    if deployed:
        print(f"Deployed: {', '.join(deployed)}")
        
        mesh = engine.drone_swarm.create_mesh(deployed)
        coverage = engine.drone_swarm.calculate_coverage(deployed)
        
        print(f"Mesh: {len(mesh)} nodes")
        print(f"Coverage: {coverage/1e6:.2f} km²")
        
        # Calculate deployment time
        times = []
        for d_id in deployed:
            drone = engine.drone_swarm.drones[d_id]
            dist = drone._distance_to(target)
            time_to_reach = dist / drone.specs.max_speed
            times.append(time_to_reach)
        
        avg_time = np.mean(times)
        print(f"Avg deployment time: {avg_time:.1f}s")
        
        return {
            'deployed': deployed,
            'mesh_size': len(mesh),
            'coverage_km2': coverage / 1e6,
            'avg_deployment_time': avg_time
        }
    else:
        print("No drones available")
        return {'error': 'No drones available'}