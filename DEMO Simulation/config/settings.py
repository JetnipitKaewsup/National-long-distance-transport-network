"""
Configuration settings for the simulation
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Central configuration management"""
    
    # Simulation parameters
    SIM_DURATION = int(os.getenv('SIM_DURATION', '3600'))
    TIME_STEP = float(os.getenv('TIME_STEP', '0.1'))
    RANDOM_SEED = int(os.getenv('RANDOM_SEED', '42'))
    
    # Network topology
    NUM_CORE_NODES = int(os.getenv('NUM_CORE_NODES', '5'))
    NUM_SATELLITES = int(os.getenv('NUM_SATELLITES', '4'))
    NUM_DRONES = int(os.getenv('NUM_DRONES', '8'))
    NUM_VEHICLES = int(os.getenv('NUM_VEHICLES', '5'))
    NUM_BASES = int(os.getenv('NUM_BASES', '5'))
    
    # 5G/6G Parameters
    CORE_BANDWIDTH_5G = int(os.getenv('CORE_BANDWIDTH_5G', '10240'))
    CORE_BANDWIDTH_6G = int(os.getenv('CORE_BANDWIDTH_6G', '102400'))
    CORE_LATENCY_5G = float(os.getenv('CORE_LATENCY_5G', '1'))
    CORE_LATENCY_6G = float(os.getenv('CORE_LATENCY_6G', '0.1'))
    CORE_RELIABILITY_5G = float(os.getenv('CORE_RELIABILITY_5G', '0.999'))
    CORE_RELIABILITY_6G = float(os.getenv('CORE_RELIABILITY_6G', '0.9999'))
    
    # Satellite Parameters
    SAT_BANDWIDTH = int(os.getenv('SAT_BANDWIDTH', '100'))
    SAT_LATENCY = float(os.getenv('SAT_LATENCY', '250'))
    SAT_RELIABILITY = float(os.getenv('SAT_RELIABILITY', '0.95'))
    
    # Drone Parameters
    DRONE_BANDWIDTH = int(os.getenv('DRONE_BANDWIDTH', '50'))
    DRONE_LATENCY = float(os.getenv('DRONE_LATENCY', '10'))
    DRONE_RELIABILITY = float(os.getenv('DRONE_RELIABILITY', '0.9'))
    DRONE_BATTERY_CAPACITY = float(os.getenv('DRONE_BATTERY_CAPACITY', '3600'))
    DRONE_CHARGE_RATE = float(os.getenv('DRONE_CHARGE_RATE', '600'))
    DRONE_MAX_SPEED = float(os.getenv('DRONE_MAX_SPEED', '15'))
    DRONE_MAX_RANGE = float(os.getenv('DRONE_MAX_RANGE', '1000'))
    DRONE_MESH_RANGE = float(os.getenv('DRONE_MESH_RANGE', '300'))
    DRONE_DISCHARGE_PATROL = float(os.getenv('DRONE_DISCHARGE_PATROL', '60'))
    DRONE_DISCHARGE_MESH = float(os.getenv('DRONE_DISCHARGE_MESH', '90'))
    ENABLE_HOT_SWAP = os.getenv('ENABLE_HOT_SWAP', 'true').lower() == 'true'
    ENABLE_AUTO_CHARGING = os.getenv('ENABLE_AUTO_CHARGING', 'true').lower() == 'true'
    
    # Handover Parameters
    HANDOVER_LATENCY_5G_TO_SAT = float(os.getenv('HANDOVER_LATENCY_5G_TO_SAT', '500'))
    HANDOVER_LATENCY_5G_TO_DRONE = float(os.getenv('HANDOVER_LATENCY_5G_TO_DRONE', '100'))
    HANDOVER_LATENCY_SAT_TO_DRONE = float(os.getenv('HANDOVER_LATENCY_SAT_TO_DRONE', '200'))
    
    # Feature flags
    ENABLE_DIGITAL_TWIN = os.getenv('ENABLE_DIGITAL_TWIN', 'true').lower() == 'true'
    ENABLE_ENCRYPTION = os.getenv('ENABLE_ENCRYPTION', 'true').lower() == 'true'
    ENABLE_REASONING = os.getenv('ENABLE_REASONING', 'true').lower() == 'true'
    REAL_TIME_PLOT = os.getenv('REAL_TIME_PLOT', 'false').lower() == 'true'
    COLLECT_METRICS = os.getenv('COLLECT_METRICS', 'true').lower() == 'true'
    
    # Output
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './simulation_output')
    SAVE_INTERVAL = int(os.getenv('SAVE_INTERVAL', '60'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()