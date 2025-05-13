import grpc
import os  # Import os to access environment variables
from vendor import superhero_pb2
from vendor import superhero_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = superhero_pb2_grpc.SuperHeroServiceStub(channel)
        access_token = os.environ.get("SUPERHERO_API_KEY")  # Load API key from environment variable
        name = "Batman"

        if not access_token:
            print("Error: SUPERHERO_API_KEY environment variable is not set.")
            return

        try:
            response = stub.SearchHero(superhero_pb2.SearchHeroRequest(access_token=access_token, name=name))
            for hero in response.heroes:
                print(f"Hero ID: {hero.id}, Name: {hero.name}, Image URL: {hero.image_url}")
        except grpc.RpcError as e:
            print(f"Error: {e.details()}")

if __name__ == "__main__":
    run()
