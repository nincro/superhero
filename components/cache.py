import random  # Import random module
import time
from collections import OrderedDict  # Import OrderedDict for LRU


class SimpleCache:
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


class LRUCache:
    def __init__(self, expiration_time=300, capacity=100):
        # expiration_time is in seconds
        self.expiration_time = expiration_time
        self.capacity = capacity  # Maximum number of items in the cache
        self.cache = OrderedDict()  # Use OrderedDict to maintain LRU order
        self.cache_hits = 0
        self.cache_misses = 0

    def get(self, key):
        if key in self.cache:
            entry = self.cache.pop(key)  # Remove and reinsert to mark as recently used
            if time.time() - entry['timestamp'] < self.expiration_time:
                self.cache_hits += 1
                self.cache[key] = entry  # Reinsert the entry
                return entry['data']
            else:
                # Invalidate expired cache
                del entry
        self.cache_misses += 1
        return None

    def set(self, key, value):
        # Add random duration (e.g., 0 to 30 seconds) to expiration time
        random_duration = random.uniform(0, 30)
        if key in self.cache:
            self.cache.pop(key)  # Remove existing entry to update it
        elif len(self.cache) >= self.capacity:
            # Evict the least recently used item
            self.cache.popitem(last=False)
        self.cache[key] = {
            'data': value,
            'timestamp': time.time() + random_duration
        }

    def clear(self):
        self.cache.clear()

    def get_cache_stats(self):
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses
        }
