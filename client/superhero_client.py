import grpc
import os
from dotenv import load_dotenv
from vendor import superhero_pb2
from vendor import superhero_pb2_grpc
from components.message_queue import MessageQueue  # Import the Redis-backed MessageQueue

def subscribe_to_updates(message_queue):
    try:
        while True:
            update = message_queue.consume()  # Consume updates from the Redis queue
            print(f"Update Notification: {update}")
    except KeyboardInterrupt:
        print("Stopped subscribing to updates.")

def run():
    load_dotenv()  # Load environment variables from .env
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = superhero_pb2_grpc.SuperHeroServiceStub(channel)
        access_token = os.environ.get("SUPERHERO_API_KEY")
        name = "Batman"

        if not access_token:
            print("Error: SUPERHERO_API_KEY environment variable is not set.")
            return

        # Use the Redis-backed queue
        message_queue = MessageQueue(redis_host="localhost", redis_port=6379)

        # Start a thread to listen for updates
        import threading
        subscribe_thread = threading.Thread(target=subscribe_to_updates, args=(message_queue,), daemon=True)
        subscribe_thread.start()

        try:
            response = stub.SearchHero(superhero_pb2.SearchHeroRequest(access_token=access_token, name=name))
            for hero in response.heroes:
                print(f"Hero ID: {hero.id}, Name: {hero.name}, Image URL: {hero.image_url}")
        except grpc.RpcError as e:
            print(f"Error: {e.details()}")

        # Wait for the subscribe thread to finish, it should be endless in this case
        subscribe_thread.join()

if __name__ == "__main__":
    run()
