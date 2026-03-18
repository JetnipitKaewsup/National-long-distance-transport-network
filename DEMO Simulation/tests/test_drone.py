"""
Unit tests for drone model
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.drone_model import Drone, DroneSwarm, DroneStatus

class TestDrone(unittest.TestCase):
    
    def setUp(self):
        self.drone = Drone("test_drone", (0, 0, 100))
        
    def test_initial_state(self):
        self.assertEqual(self.drone.id, "test_drone")
        self.assertEqual(self.drone.position, (0, 0, 100))
        self.assertEqual(self.drone.battery_level, 3600)
        self.assertTrue(self.drone.is_active)
        
    def test_battery_drain(self):
        self.drone.status = DroneStatus.PATROLLING
        self.drone.update_battery(60, False)
        self.assertLess(self.drone.battery_level, 3600)
        
    def test_battery_charge(self):
        self.drone.battery_level = 1800
        self.drone.status = DroneStatus.CHARGING
        self.drone.update_battery(60, False)
        self.assertGreater(self.drone.battery_level, 1800)
        
    def test_can_reach(self):
        self.assertTrue(self.drone.can_reach((100, 0, 100)))
        self.drone.battery_level = 100
        self.assertFalse(self.drone.can_reach((1000, 0, 100)))

class TestDroneSwarm(unittest.TestCase):
    
    def setUp(self):
        self.swarm = DroneSwarm()
        for i in range(3):
            drone = Drone(f"drone_{i}", (i*100, 0, 100))
            self.swarm.add_drone(drone)
            
    def test_add_drone(self):
        self.assertEqual(len(self.swarm.drones), 3)
        
    def test_deploy_swarm(self):
        deployed = self.swarm.deploy_swarm((500, 500, 100), 2)
        self.assertEqual(len(deployed), 2)
        
    def test_create_mesh(self):
        drone_ids = list(self.swarm.drones.keys())
        mesh = self.swarm.create_mesh(drone_ids)
        self.assertEqual(len(mesh), 3)
        
    def test_coverage(self):
        coverage = self.swarm.calculate_coverage()
        self.assertGreater(coverage, 0)

if __name__ == '__main__':
    unittest.main()