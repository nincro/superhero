import requests
import random  # Import random for generating random updates

class SuperHeroAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def search_hero(self, access_token, name):
        # This one is actually calling superhero's Restful API
        url = f"{self.base_url}/{access_token}/search/{name}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_updates(self):
        # I didn't find the API that will provide the update so I choose to mock it here haha.
        print("Fetching updates from the SuperHero API...")
        # Make some random changes
        updates = [
            {"id": "1", "name": "Batman", "powerstats": {"intelligence": random.randint(80, 100)}},
            {"id": "2", "name": "Superman", "powerstats": {"strength": random.randint(90, 100)}},
        ]
        # Randomly select one or more heroes to update
        return random.sample(updates, random.randint(1, len(updates)))
