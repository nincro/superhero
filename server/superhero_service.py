from concurrent import futures
import grpc
import threading
import time
import requests
import queue
from dotenv import load_dotenv  # Import dotenv

from cache import Cache
from api_client import SuperHeroAPIClient
from vendor import superhero_pb2
from vendor import superhero_pb2_grpc


class SuperHeroService(superhero_pb2_grpc.SuperHeroServiceServicer):
    def __init__(self, api_client, cache):
        # Dependency injection for API client and cache
        self.api_client = api_client
        self.cache = cache
        self.subscribers = []  # List to store active subscribers

    def SubscribeUpdates(self, request, context):
        access_token = request.access_token

        if not access_token:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Access token is required.")
            return

        # Add the subscriber to the list
        subscriber_queue = queue.Queue()
        self.subscribers.append(subscriber_queue)
        print(f"New subscriber added for access token: {access_token}")

        try:
            # Start to poll the update
            while True:
                update = subscriber_queue.get()
                yield superhero_pb2.UpdateNotification(message=update)
        except Exception as e:
            print(f"Subscriber disconnected: {e}")
        finally:
            # Remove the subscriber when the client exits or something
            self.subscribers.remove(subscriber_queue)
            print(f"Subscriber removed for access token: {access_token}")

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
    # Register the service
    superhero_pb2_grpc.add_SuperHeroServiceServicer_to_server(service, server)
    server.add_insecure_port("[::]:50051")
    print("Server running on port 50051")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Server stopped")


##### Sub Modules #####
def log_cache_stats(cache):
    while True:
        stats = cache.get_cache_stats()
        print(f"Cache Stats - Hits: {stats['hits']}, Misses: {stats['misses']}")
        time.sleep(5)


def poll_for_updates(api_client, cache, subscribers):
    # Poll the SuperHero API for updates
    while True:
        try:
            print("Polling for updates...")
            updates = api_client.get_updates()  # Fetch updates
            for update in updates:
                cache.set(update["id"], update)  # Update the cache
                update_message = f"Update for character: {update['name']}"
                for subscriber in subscribers:
                    subscriber.put(update_message)  # Push update to all subscribers
                    print(f"Broadcasted update: {update_message}")
        except Exception as e:
            print(f"Error during polling: {e}")
        time.sleep(10)  # Poll every 10 seconds


if __name__ == "__main__":
    api_client = SuperHeroAPIClient(base_url="https://superheroapi.com/api")
    # Initial components
    cache = Cache(expiration_time=300)

    # Run modules
    # Module for statistic of caching
    threading.Thread(target=log_cache_stats, args=(cache,), daemon=True).start()

    # Module for polling the update from superheros server (mock)
    service = SuperHeroService(api_client=api_client, cache=cache)
    threading.Thread(
        target=poll_for_updates, args=(api_client, cache, service.subscribers), daemon=True
    ).start()

    serve(service)
