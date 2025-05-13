from concurrent import futures
import grpc
import threading
import time

import requests

from cache import Cache
from api_client import SuperHeroAPIClient
from vendor import superhero_pb2
from vendor import superhero_pb2_grpc

class SuperHeroService(superhero_pb2_grpc.SuperHeroServiceServicer):
    def __init__(self, api_client, cache):
        # Dependency injection for API client and cache
        self.api_client = api_client
        self.cache = cache

    def SearchHero(self, request, context):
        access_token = request.access_token
        name = request.name

        # Check cache first
        cache_key = f"{access_token}:{name}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            print(f"Cache hit for term: {name}")
            return cached_data

        # Cache miss, fetch from API
        print(f"Cache miss for term: {name}")
        try:
            data = self.api_client.search_hero(access_token, name)

            # Transform the REST API response to gRPC-compatible format
            heroes = [
                superhero_pb2.Hero(
                    id=hero["id"],
                    name=hero["name"],
                    powerstats=str(hero["powerstats"]),
                    biography=str(hero["biography"]),
                    appearance=str(hero["appearance"]),
                    work=str(hero["work"]),
                    connections=str(hero["connections"]),
                    image_url=hero["image"]["url"],
                )
                for hero in data.get("results", [])
            ]

            # Cache the response
            grpc_response = superhero_pb2.SearchHeroResponse(heroes=heroes)
            self.cache.set(cache_key, grpc_response)
            return grpc_response
        except requests.RequestException as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return superhero_pb2.SearchHeroResponse()


def serve(service):
    print("Starting gRPC server...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    superhero_pb2_grpc.add_SuperHeroServiceServicer_to_server(service, server)
    server.add_insecure_port("[::]:50051")
    print("Server running on port 50051")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Server stopped")

def log_cache_stats(cache):
    while True:
        stats = cache.get_cache_stats()
        print(f"Cache Stats - Hits: {stats['hits']}, Misses: {stats['misses']}")
        time.sleep(5)

if __name__ == "__main__":
    api_client = SuperHeroAPIClient(base_url="https://superheroapi.com/api")

    cache = Cache(expiration_time=300)
    threading.Thread(target=log_cache_stats, args=(cache,), daemon=True).start()

    service = SuperHeroService(api_client=api_client, cache=cache)
    serve(service)
