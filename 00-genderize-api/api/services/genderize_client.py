import requests


class GenderizeClient:
    BASE_URL = "https://api.genderize.io"
    TIMEOUT = 10

    @staticmethod
    def fetch_gender_data(name: str):
        """Fetch gender prediction from Genderize API"""
        try:
            response = requests.get(
                f"{GenderizeClient.BASE_URL}",
                params={"name": name},
                timeout=GenderizeClient.TIMEOUT,
            )

            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException:
            return None
