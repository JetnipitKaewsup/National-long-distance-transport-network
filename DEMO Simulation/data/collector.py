"""
Data collection for simulation metrics
"""
import time
from typing import Dict, List, Any
from collections import defaultdict
import json

class DataCollector:
    """Collect and store simulation data"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.snapshots = []
        
    def record_metric(self, name: str, value: float, tags: Dict = None):
        """Record a metric value"""
        self.metrics[name].append({
            'time': time.time(),
            'value': value,
            'tags': tags or {}
        })
    
    def record_snapshot(self, data: Dict):
        """Record a system snapshot"""
        self.snapshots.append({
            'time': time.time(),
            'data': data
        })
    
    def get_metric(self, name: str, start_time: float = None, 
                   end_time: float = None) -> List[Dict]:
        """Get metric values within time range"""
        values = self.metrics.get(name, [])
        
        if start_time is not None:
            values = [v for v in values if v['time'] >= start_time]
        if end_time is not None:
            values = [v for v in values if v['time'] <= end_time]
            
        return values
    
    def get_snapshots(self, n: int = None) -> List[Dict]:
        """Get recent snapshots"""
        if n is None:
            return self.snapshots
        return self.snapshots[-n:]
    
    def export_to_json(self, filename: str):
        """Export data to JSON file"""
        data = {
            'metrics': dict(self.metrics),
            'snapshots': self.snapshots
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def clear(self):
        """Clear all collected data"""
        self.metrics.clear()
        self.snapshots.clear()