import requests

class NationalizeClient:
    BASE_URL = 'https://api.nationalize.io'
    TIMEOUT = 10

    @staticmethod
    def fetch_nationality_data(name: str):
        try:
            response = requests.get(
                NationalizeClient.BASE_URL,
                params={'name': name},
                timeout=NationalizeClient.TIMEOUT
            )

            response.raise_for_status()
            data = response.json()

            # Edge case: no country data
            if not data.get("country") or len(data["country"]) == 0:
                return None
            
            # Pick top country with highest probability
            top_country = max(data["country"], key=lambda x: x["probability"])
            
            return {
                "country_id": top_country["country_id"],
                "country_probability": top_country["probability"]
            }
        except requests.RequestException:
            return None