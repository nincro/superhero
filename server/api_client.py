import requests

class SuperHeroAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def search_hero(self, access_token, name):
        url = f"{self.base_url}/{access_token}/search/{name}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
