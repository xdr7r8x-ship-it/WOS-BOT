import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta


class RateLimiter:
    def __init__(self):
        self._locks = defaultdict(threading.RLock)
        self._request_times = defaultdict(list)
        self._circuit_breakers = defaultdict(lambda: {
            "failures": 0,
            "type": None,
            "paused_until": None
        })
    
    def acquire(self, key: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        with self._locks[key]:
            now = time.time()
            cutoff = now - window_seconds
            self._request_times[key] = [
                t for t in self._request_times[key] if t > cutoff
            ]
            
            if len(self._request_times[key]) >= max_requests:
                return False
            
            self._request_times[key].append(now)
            return True
    
    def wait_if_needed(self, key: str, max_requests: int = 10, window_seconds: int = 60):
        while not self.acquire(key, max_requests, window_seconds):
            time.sleep(0.5)
    
    def record_failure(self, guild_id: str, error_type: str):
        cb = self._circuit_breakers[guild_id]
        
        if cb["type"] != error_type:
            cb["failures"] = 1
            cb["type"] = error_type
        else:
            cb["failures"] += 1
        
        threshold_network = 10
        threshold_timeout = 5
        threshold_rate = 5
        
        threshold = {
            "NETWORK_ERROR": threshold_network,
            "TIMEOUT": threshold_timeout,
            "RATE_LIMIT": threshold_rate,
        }.get(error_type, 5)
        
        if cb["failures"] >= threshold:
            cb["paused_until"] = datetime.utcnow() + timedelta(minutes=10)
    
    def is_paused(self, guild_id: str) -> tuple[bool, str]:
        cb = self._circuit_breakers[guild_id]
        
        if cb["paused_until"] and datetime.utcnow() < cb["paused_until"]:
            remaining = (cb["paused_until"] - datetime.utcnow()).total_seconds()
            return True, f"Paused for {int(remaining)}s ({cb['type']})"
        
        return False, ""
    
    def reset_circuit(self, guild_id: str):
        self._circuit_breakers[guild_id] = {
            "failures": 0,
            "type": None,
            "paused_until": None
        }
    
    def check_and_wait(self, guild_id: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        is_paused, msg = self.is_paused(guild_id)
        if is_paused:
            return False
        
        self.wait_if_needed(guild_id, max_requests, window_seconds)
        return True


rate_limiter = RateLimiter()
