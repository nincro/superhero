import time
import random  # Import random module

class Cache:
    def __init__(self, expiration_time=300):
        # expiration_time is in seconds
        self.expiration_time = expiration_time
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def get(self, key):
        if key in self.cache:
            entry = self.cache[key]

            if time.time() - entry['timestamp'] < self.expiration_time:
                self.cache_hits += 1
                return entry['data']
            else:
                # Invalidate expired cache
                del self.cache[key]
        self.cache_misses += 1
        return None

    def set(self, key, value):
        # Add random duration (e.g., 0 to 30 seconds) to expiration time
        # prevent a large caching missing
        random_duration = random.uniform(0, 30)
        self.cache[key] = {
            'data': value,
            'timestamp': time.time() + random_duration
        }

    def clear(self):
        self.cache = {}

    def get_cache_stats(self):
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses
        }
