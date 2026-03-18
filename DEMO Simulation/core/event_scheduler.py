"""
Event-driven simulation scheduler
"""
import heapq
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Types of simulation events"""
    PACKET_GENERATION = "packet_generation"
    PACKET_TRANSMISSION = "packet_transmission"
    PACKET_ARRIVAL = "packet_arrival"
    NODE_MOVEMENT = "node_movement"
    BATTERY_UPDATE = "battery_update"
    HANDOVER_CHECK = "handover_check"
    EMERGENCY_CHECK = "emergency_check"
    STATISTICS_UPDATE = "statistics_update"
    DIGITAL_TWIN_SYNC = "digital_twin_sync"

@dataclass
class Event:
    """Simulation event"""
    time: float
    event_type: EventType
    callback: Callable
    data: Optional[Dict] = None
    priority: int = 0
    
    def __lt__(self, other):
        return self.time < other.time

class EventScheduler:
    """Event-driven scheduler for simulation"""
    
    def __init__(self):
        self.events: List[Event] = []
        self.current_time = 0.0
        self.event_count = 0
        self.event_history: List[Dict] = []
        self.max_history = 10000
        
    def schedule(self, delay: float, event_type: EventType, 
                 callback: Callable, data: Dict = None, 
                 priority: int = 0) -> Event:
        """Schedule an event after delay seconds"""
        event_time = self.current_time + delay
        event = Event(
            time=event_time,
            event_type=event_type,
            callback=callback,
            data=data,
            priority=priority
        )
        heapq.heappush(self.events, event)
        self.event_count += 1
        return event
    
    def schedule_absolute(self, time: float, event_type: EventType,
                         callback: Callable, data: Dict = None,
                         priority: int = 0) -> Event:
        """Schedule an event at absolute time"""
        event = Event(
            time=time,
            event_type=event_type,
            callback=callback,
            data=data,
            priority=priority
        )
        heapq.heappush(self.events, event)
        self.event_count += 1
        return event
    
    def run(self, duration: float, step_callback: Callable = None):
        """Run simulation for specified duration"""
        end_time = self.current_time + duration
        last_step_time = self.current_time
        
        logger.info(f"Starting simulation: {self.current_time:.2f}s -> {end_time:.2f}s")
        
        while self.events and self.current_time <= end_time:
            event = heapq.heappop(self.events)
            self.current_time = event.time
            
            # Record event
            self.event_history.append({
                'time': self.current_time,
                'type': event.event_type.value
            })
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
            
            # Execute event
            try:
                result = event.callback(event.data)
                
                # Reschedule periodic events
                if event.data and event.data.get('periodic'):
                    interval = event.data.get('interval', 1.0)
                    self.schedule(
                        delay=interval,
                        event_type=event.event_type,
                        callback=event.callback,
                        data={**event.data, 'periodic': True, 'interval': interval},
                        priority=event.priority
                    )
            except Exception as e:
                logger.error(f"Event error at t={self.current_time:.2f}: {e}")
            
            # Call step callback
            if step_callback and self.current_time - last_step_time >= 1.0:
                step_callback(self.current_time)
                last_step_time = self.current_time
        
        logger.info(f"Starting simulation: {self.current_time:.2f}s -> {end_time:.2f}s")
    
    def reset(self):
        """Reset scheduler"""
        self.events = []
        self.current_time = 0.0
        self.event_count = 0
        self.event_history = []
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics"""
        return {
            'current_time': self.current_time,
            'events_processed': self.event_count,
            'events_pending': len(self.events),
            'history_size': len(self.event_history)
        }