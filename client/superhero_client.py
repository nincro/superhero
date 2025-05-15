import os

import grpc
from dotenv import load_dotenv

from vendor import superhero_pb2
from vendor import superhero_pb2_grpc


def subscribe_to_updates(stub, access_token):
    try:
        for update in stub.SubscribeUpdates(superhero_pb2.SubscribeUpdatesRequest(access_token=access_token)):
            print(f"Update Notification: {update.message}")
    except grpc.RpcError as e:
        print(f"Error while subscribing to updates: {e.details()}")


def run():
    load_dotenv()  # Load environment variables from .env
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = superhero_pb2_grpc.SuperHeroServiceStub(channel)
        access_token = os.environ.get("SUPERHERO_API_KEY")
        name = "Batman"

        if not access_token:
            print("Error: SUPERHERO_API_KEY environment variable is not set.")
            return

        # Start a thread to listen for updates
        import threading
        polling_thread = threading.Thread(target=subscribe_to_updates, args=(stub, access_token), daemon=True)
        polling_thread.start()

        try:
            response = stub.SearchHero(superhero_pb2.SearchHeroRequest(access_token=access_token, name=name))
            for hero in response.heroes:
                print(f"Hero ID: {hero.id}, Name: {hero.name}, Image URL: {hero.image_url}")
        except grpc.RpcError as e:
            print(f"Error: {e.details()}")

        # Wait for the polling_thread to finish, it should be endless in this case
        polling_thread.join()


if __name__ == "__main__":
    run()
