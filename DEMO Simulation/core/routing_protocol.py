"""
Routing protocols for network simulation
"""
from typing import Dict, List, Optional, Set
from collections import deque
import heapq

class RoutingProtocol:
    """Routing algorithms for network"""
    
    def __init__(self):
        self.route_cache = {}
        self.cache_timeout = 60  # seconds
        
    def find_path(self, source: str, destination: str, 
                  nodes: Dict, priority: int = 3) -> Optional[List[str]]:
        """Find path between nodes using BFS"""
        if source == destination:
            return [source]
        
        # Check cache
        cache_key = f"{source}-{destination}"
        if cache_key in self.route_cache:
            return self.route_cache[cache_key]
        
        # BFS
        visited = {source}
        queue = deque([(source, [source])])
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in nodes[current].connections:
                if neighbor not in visited:
                    if neighbor == destination:
                        full_path = path + [neighbor]
                        self.route_cache[cache_key] = full_path
                        return full_path
                    
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def find_all_paths(self, source: str, destination: str,
                       nodes: Dict) -> List[List[str]]:
        """Find all possible paths"""
        paths = []
        visited = set()
        
        def dfs(current: str, path: List[str]):
            if current == destination:
                paths.append(path.copy())
                return
            
            for neighbor in nodes[current].connections:
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, path)
                    path.pop()
                    visited.remove(neighbor)
        
        visited.add(source)
        dfs(source, [source])
        
        return paths
    
    def find_shortest_path(self, source: str, destination: str,
                          nodes: Dict) -> Optional[List[str]]:
        """Find shortest path using Dijkstra"""
        distances = {node: float('inf') for node in nodes}
        previous = {node: None for node in nodes}
        distances[source] = 0
        
        pq = [(0, source)]
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current == destination:
                break
            
            if current_dist > distances[current]:
                continue
            
            for neighbor in nodes[current].connections:
                # Assume each hop costs 1
                distance = current_dist + 1
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct path
        if distances[destination] == float('inf'):
            return None
        
        path = []
        current = destination
        while current:
            path.append(current)
            current = previous[current]
        
        return path[::-1]
    
    def clear_cache(self):
        """Clear route cache"""
        self.route_cache.clear()